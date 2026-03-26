from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.api import deps
from app.models.post import Post, Comment, PostLike
from app.models.user import User
from app.models.social import Notification
from app.api.v1.chat import manager
from app.schemas.post import PostCreate, PostResponse, PostDetailResponse, CommentCreate, CommentResponse

router = APIRouter()

@router.get("/", response_model=List[PostResponse])
def read_posts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    posts = db.query(Post).options(joinedload(Post.author)).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.post("/", response_model=PostResponse)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: PostCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    post = Post(
        title=post_in.title,
        content=post_in.content,
        cover_image=post_in.cover_image,
        author_id=current_user.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post.id).first()
    return post

@router.get("/{id}", response_model=PostDetailResponse)
def read_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    post = db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.comments).joinedload(Comment.author)
    ).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    post.views += 1
    db.commit()
    db.refresh(post)
    return post

@router.post("/{id}/like")
async def like_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    existing_like = db.query(PostLike).filter(
        PostLike.post_id == id,
        PostLike.user_id == current_user.id
    ).first()

    if existing_like:
        db.delete(existing_like)
        post.likes = max(0, post.likes - 1)
        db.commit()
        return {"likes_count": post.likes, "is_liked": False}
    else:
        new_like = PostLike(user_id=current_user.id, post_id=id)
        db.add(new_like)
        post.likes += 1

        if post.author_id != current_user.id:
            notification = Notification(
                user_id=post.author_id,
                sender_id=current_user.id,
                type="like_post",
                content=f"{current_user.username} 赞了你的文章《{post.title}》"
            )
            db.add(notification)

            await manager.send_personal_message({
                "type": "notification",
                "action": "like_post",
                "sender": current_user.username,
                "post_id": post.id
            }, post.author_id)

        db.commit()
        return {"likes_count": post.likes, "is_liked": True}

@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    post = db.query(Post).filter(Post.id == comment_in.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    comment = Comment(
        content=comment_in.content,
        post_id=comment_in.post_id,
        parent_id=comment_in.parent_id,
        author_id=current_user.id
    )
    db.add(comment)

    target_user_id = post.author_id
    if comment_in.parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == comment_in.parent_id).first()
        if parent_comment:
            target_user_id = parent_comment.author_id

    if target_user_id != current_user.id:
        notification = Notification(
            user_id=target_user_id,
            sender_id=current_user.id,
            type="comment",
            content=f"{current_user.username} 评论了你的文章《{post.title}》"
        )
        db.add(notification)

        await manager.send_personal_message({
            "type": "notification",
            "action": "comment",
            "sender": current_user.username,
            "post_id": post.id
        }, target_user_id)

    db.commit()
    db.refresh(comment)
    comment = db.query(Comment).options(joinedload(Comment.author)).filter(Comment.id == comment.id).first()
    return comment
