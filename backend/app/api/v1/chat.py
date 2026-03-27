import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.api import deps
from app.models.social import Message, Friendship, Notification
from app.models.user import User
from app.models.post import Post
from app.schemas.social import FriendRequestCreate, FriendshipResponse, NotificationResponse
from typing import List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
            return True
        return False

manager = ConnectionManager()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(deps.get_db)):
    user = await deps.get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action")

            if action == "send_message":
                receiver_id = payload.get("receiver_id")
                content = payload.get("content")
                temp_id = payload.get("temp_id")

                is_friend = db.query(Friendship).filter(
                    or_(
                        and_(Friendship.user_id == user.id, Friendship.friend_id == receiver_id),
                        and_(Friendship.user_id == receiver_id, Friendship.friend_id == user.id)
                    ),
                    Friendship.status == "accepted"
                ).first()

                if not is_friend:
                    await manager.send_personal_message({"type": "error", "content": "你们还不是好友"}, user.id)
                    continue

                new_msg = Message(sender_id=user.id, receiver_id=receiver_id, content=content)
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)

                await manager.send_personal_message({
                    "type": "ack",
                    "temp_id": temp_id,
                    "id": new_msg.id,
                    "created_at": str(new_msg.created_at)
                }, user.id)

                await manager.send_personal_message({
                    "type": "chat",
                    "id": new_msg.id,
                    "sender_id": user.id,
                    "receiver_id": receiver_id,
                    "content": content,
                    "created_at": str(new_msg.created_at)
                }, receiver_id)

            elif action == "heartbeat":
                pass

    except WebSocketDisconnect:
        manager.disconnect(user.id)

@router.get("/friends")
def get_friends(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    friendships = db.query(Friendship).filter(
        or_(Friendship.user_id == current_user.id, Friendship.friend_id == current_user.id),
        Friendship.status == "accepted"
    ).all()

    friends = []
    for f in friendships:
        friend_id = f.friend_id if f.user_id == current_user.id else f.user_id
        friend = db.query(User).filter(User.id == friend_id).first()
        if friend:
            # Get last message visible to current_user
            last_msg = db.query(Message).filter(
                or_(
                    and_(Message.sender_id == current_user.id, Message.receiver_id == friend_id, Message.deleted_by_sender == False),
                    and_(Message.sender_id == friend_id, Message.receiver_id == current_user.id, Message.deleted_by_receiver == False)
                )
            ).order_by(Message.created_at.desc()).first()

            # Get unread count
            unread_count = db.query(Message).filter(
                Message.sender_id == friend_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False,
                Message.deleted_by_receiver == False
            ).count()

            friends.append({
                "id": friend.id,
                "username": friend.username,
                "avatar": friend.avatar,
                "level": friend.level,
                "online": friend.id in manager.active_connections,
                "last_message": last_msg.content if last_msg else None,
                "last_message_time": last_msg.created_at if last_msg else None,
                "unread_count": unread_count
            })
            
    # Sort friends by last message time (recent first)
    friends.sort(key=lambda x: x["last_message_time"] or datetime.min, reverse=True)
    return friends

@router.post("/friend-request/{user_id}")
async def send_friend_request(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    existing = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == user_id),
            and_(Friendship.user_id == user_id, Friendship.friend_id == current_user.id)
        )
    ).first()

    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="已经是好友了")
        elif existing.status == "pending":
            if existing.user_id == current_user.id:
                raise HTTPException(status_code=400, detail="已发送过好友请求，等待对方确认")
            else:
                existing.status = "accepted"
                db.commit()
                return {"message": "已同意好友请求"}

    friendship = Friendship(user_id=current_user.id, friend_id=user_id, status="pending")
    db.add(friendship)

    notification = Notification(
        user_id=user_id,
        sender_id=current_user.id,
        type="friend_request",
        content=f"{current_user.username} 请求添加你为好友"
    )
    db.add(notification)

    await manager.send_personal_message({
        "type": "notification",
        "action": "friend_request",
        "sender": current_user.username
    }, user_id)

    db.commit()
    return {"message": "好友请求已发送"}

@router.put("/friend-request/{user_id}/accept")
async def accept_friend_request(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    friendship = db.query(Friendship).filter(
        Friendship.user_id == user_id,
        Friendship.friend_id == current_user.id,
        Friendship.status == "pending"
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="没有找到该好友请求")

    friendship.status = "accepted"

    notification = Notification(
        user_id=user_id,
        sender_id=current_user.id,
        type="friend_request_accepted",
        content=f"{current_user.username} 同意了你的好友请求"
    )
    db.add(notification)

    await manager.send_personal_message({
        "type": "notification",
        "action": "friend_request_accepted",
        "sender": current_user.username
    }, user_id)

    db.commit()
    return {"message": "已同意好友请求"}

@router.put("/friend-request/{user_id}/reject")
def reject_friend_request(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    friendship = db.query(Friendship).filter(
        Friendship.user_id == user_id,
        Friendship.friend_id == current_user.id,
        Friendship.status == "pending"
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="没有找到该好友请求")

    # Change status to rejected or just delete it
    db.delete(friendship)
    
    # Mark the notification as read so it doesn't prompt again
    notification = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.sender_id == user_id,
        Notification.type == "friend_request"
    ).first()
    if notification:
        notification.is_read = True

    db.commit()
    return {"message": "已拒绝好友请求"}

@router.delete("/friend/{user_id}")
def remove_friend(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == user_id),
            and_(Friendship.user_id == user_id, Friendship.friend_id == current_user.id)
        ),
        Friendship.status == "accepted"
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="不是好友关系")

    db.delete(friendship)
    db.commit()
    return {"message": "已解除好友关系"}

@router.get("/friend-status/{user_id}")
def get_friend_status(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == user_id),
            and_(Friendship.user_id == user_id, Friendship.friend_id == current_user.id)
        )
    ).first()

    if not friendship:
        return {"status": "none"}
    if friendship.status == "accepted":
        return {"status": "accepted"}
    if friendship.status == "pending":
        if friendship.user_id == current_user.id:
            return {"status": "pending_sent"}
        else:
            return {"status": "pending_received"}
    return {"status": friendship.status}

@router.get("/users/{user_id}/stats")
def get_user_stats(
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    followers_count = db.query(Friendship).filter(
        Friendship.friend_id == user_id,
        Friendship.status == "accepted"
    ).count()

    following_count = db.query(Friendship).filter(
        Friendship.user_id == user_id,
        Friendship.status == "accepted"
    ).count()

    posts_count = db.query(Post).filter(Post.author_id == user_id).count()

    return {
        "followers": followers_count,
        "following": following_count,
        "posts": posts_count
    }

@router.post("/friends/request")
async def send_friend_request(
    request_data: FriendRequestCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    if request_data.friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")

    existing = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == request_data.friend_id),
            and_(Friendship.user_id == request_data.friend_id, Friendship.friend_id == current_user.id)
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"好友关系已存在: {existing.status}")

    friendship = Friendship(user_id=current_user.id, friend_id=request_data.friend_id, status="pending")
    db.add(friendship)

    notification = Notification(
        user_id=request_data.friend_id,
        sender_id=current_user.id,
        type="friend_request",
        content=f"{current_user.username} 请求加你为好友"
    )
    db.add(notification)
    db.commit()

    await manager.send_personal_message({
        "type": "notification",
        "action": "friend_request",
        "sender": current_user.username
    }, request_data.friend_id)

    return {"msg": "好友请求已发送"}

@router.post("/friends/accept/{sender_id}")
async def accept_friend_request(
    sender_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    friendship = db.query(Friendship).filter(
        Friendship.user_id == sender_id,
        Friendship.friend_id == current_user.id,
        Friendship.status == "pending"
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="请求不存在或已处理")

    friendship.status = "accepted"

    notification = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.sender_id == sender_id,
        Notification.type == "friend_request"
    ).first()
    if notification:
        notification.is_read = True

    db.commit()

    await manager.send_personal_message({
        "type": "notification",
        "action": "friend_accepted",
        "friend": current_user.username
    }, friendship.user_id)

    return {"msg": "已同意好友请求"}

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    # Mark as read
    for n in notifications:
        if not n.is_read:
            n.is_read = True
    db.commit()

    return notifications

@router.get("/messages/{friend_id}")
def get_messages(
    friend_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == friend_id, Message.deleted_by_sender == False),
            and_(Message.sender_id == friend_id, Message.receiver_id == current_user.id, Message.deleted_by_receiver == False)
        )
    ).order_by(Message.created_at.asc()).all()

    # Mark as read
    unread_messages = [m for m in messages if m.receiver_id == current_user.id and not m.is_read]
    if unread_messages:
        for m in unread_messages:
            m.is_read = True
        db.commit()

    return messages

@router.delete("/messages/single/{message_id}")
def delete_single_message(
    message_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")

    if msg.sender_id == current_user.id:
        msg.deleted_by_sender = True
    elif msg.receiver_id == current_user.id:
        msg.deleted_by_receiver = True
    else:
        raise HTTPException(status_code=403, detail="无权删除该消息")

    db.commit()
    return {"message": "消息已删除"}

@router.delete("/messages/{friend_id}")
def clear_messages(
    friend_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
):
    # Mark messages sent by current_user to friend_id as deleted_by_sender
    sent_msgs = db.query(Message).filter(
        Message.sender_id == current_user.id,
        Message.receiver_id == friend_id,
        Message.deleted_by_sender == False
    ).all()
    for m in sent_msgs:
        m.deleted_by_sender = True

    # Mark messages received by current_user from friend_id as deleted_by_receiver
    recv_msgs = db.query(Message).filter(
        Message.sender_id == friend_id,
        Message.receiver_id == current_user.id,
        Message.deleted_by_receiver == False
    ).all()
    for m in recv_msgs:
        m.deleted_by_receiver = True

    db.commit()
    return {"message": "聊天记录已清空"}
