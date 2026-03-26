import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.api import deps
from app.models.social import Message, Friendship, Notification
from app.models.user import User
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
                
                # Check if they are friends
                is_friend = db.query(Friendship).filter(
                    or_(
                        and_(Friendship.user_id == user.id, Friendship.friend_id == receiver_id),
                        and_(Friendship.user_id == receiver_id, Friendship.friend_id == user.id)
                    ),
                    Friendship.status == "accepted"
                ).first()
                
                if not is_friend:
                    await manager.send_personal_message({"type": "error", "content": "You are not friends"}, user.id)
                    continue

                new_msg = Message(sender_id=user.id, receiver_id=receiver_id, content=content)
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)
                
                msg_data = {
                    "type": "chat",
                    "id": new_msg.id,
                    "sender_id": user.id,
                    "content": content,
                    "created_at": str(new_msg.created_at)
                }
                
                await manager.send_personal_message(msg_data, receiver_id)
                
            elif action == "heartbeat":
                pass

    except WebSocketDisconnect:
        manager.disconnect(user.id)

@router.get("/friends")
def get_friends(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
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
            friends.append({
                "id": friend.id,
                "username": friend.username,
                "avatar": friend.avatar,
                "online": friend.id in manager.active_connections
            })
    return friends

@router.post("/friends/request")
async def send_friend_request(
    request_data: FriendRequestCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if request_data.friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")
        
    existing = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == request_data.friend_id),
            and_(Friendship.user_id == request_data.friend_id, Friendship.friend_id == current_user.id)
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Friendship status is already: {existing.status}")

    friendship = Friendship(user_id=current_user.id, friend_id=request_data.friend_id, status="pending")
    db.add(friendship)
    
    notification = Notification(
        user_id=request_data.friend_id,
        sender_id=current_user.id,
        type="friend_request",
        content=f"{current_user.username} sent you a friend request"
    )
    db.add(notification)
    db.commit()
    
    # WebSocket notification
    await manager.send_personal_message({
        "type": "notification",
        "action": "friend_request",
        "sender": current_user.username
    }, request_data.friend_id)
    
    return {"msg": "Friend request sent"}

@router.post("/friends/accept/{sender_id}")
async def accept_friend_request(
    sender_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    friendship = db.query(Friendship).filter(
        Friendship.user_id == sender_id, 
        Friendship.friend_id == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Request not found or already processed")
        
    friendship.status = "accepted"
    
    # Mark notification as read
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
    
    return {"msg": "Friend request accepted"}

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

@router.get("/messages/{friend_id}")
def get_messages(
    friend_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == friend_id),
            and_(Message.sender_id == friend_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    return messages