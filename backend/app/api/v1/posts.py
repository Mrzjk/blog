import os
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from app.api import deps
from app.models.post import Post, Comment, PostLike, PostBookmark, Tag
from app.models.user import User
from app.models.social import Notification
from app.api.v1.chat import manager
from app.schemas.post import PostCreate, PostResponse, PostDetailResponse, CommentCreate, CommentResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    return {"url": f"/uploads/{filename}"}

def get_current_user_optional(db: Session = Depends(deps.get_db), token: str = Depends(deps.oauth2_scheme)) -> Optional[User]:
    return deps.get_current_user(db, token)

@router.get("/", response_model=List[PostResponse])
def read_posts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    query = db.query(Post).filter(Post.status == "published")
    
    if search:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )
        
    posts = (
        query
        .options(joinedload(Post.author), joinedload(Post.tags), joinedload(Post.category))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    if current_user:
        post_ids = [post.id for post in posts]
        liked_ids = set()
        bookmarked_ids = set()
        if post_ids:
            liked_ids = {
                row[0]
                for row in db.query(PostLike.post_id)
                .filter(PostLike.user_id == current_user.id, PostLike.post_id.in_(post_ids))
                .all()
            }
            bookmarked_ids = {
                row[0]
                for row in db.query(PostBookmark.post_id)
                .filter(PostBookmark.user_id == current_user.id, PostBookmark.post_id.in_(post_ids))
                .all()
            }
        for post in posts:
            post.is_liked = post.id in liked_ids
            post.is_bookmarked = post.id in bookmarked_ids
    else:
        for post in posts:
            post.is_liked = False
            post.is_bookmarked = False
    return posts


@router.get("/hot", response_model=List[PostResponse])
def read_hot_posts(
    db: Session = Depends(deps.get_db),
    limit: int = 10,
) -> Any:
    """获取热门博客，按浏览量和点赞数排序"""
    posts = (
        db.query(Post)
        .filter(Post.status == "published")
        .options(joinedload(Post.author), joinedload(Post.tags), joinedload(Post.category))
        .order_by(Post.views.desc(), Post.likes.desc())
        .limit(limit)
        .all()
    )
    return posts

@router.get("/tags")
def read_tags(
    db: Session = Depends(deps.get_db),
    limit: int = 50,
) -> Any:
    """获取所有标签，带有数量统计"""
    rows = (
        db.query(Tag.name, func.count(Post.id))
        .select_from(Tag)
        .join(Tag.posts, isouter=True)
        .group_by(Tag.name)
        .order_by(func.count(Post.id).desc(), Tag.name.asc())
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


@router.get("/archive")
def archive(db: Session = Depends(deps.get_db)) -> Any:
    dialect = db.bind.dialect.name
    if dialect == "sqlite":
        month_key = func.strftime("%Y-%m", Post.created_at)
    else:
        month_key = func.to_char(Post.created_at, "YYYY-MM")

    rows = (
        db.query(month_key.label("month"), func.count(Post.id).label("count"))
        .group_by("month")
        .order_by(func.max(Post.created_at).desc())
        .all()
    )
    return [{"month": month, "count": count} for month, count in rows]


@router.get("/tag/{tag_name}", response_model=List[PostResponse])
def posts_by_tag(
    tag_name: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    tag = db.query(Tag).filter(Tag.name == tag_name.strip()).first()
    if not tag:
        return []

    posts = (
        db.query(Post)
        .join(Post.tags)
        .filter(Tag.id == tag.id, Post.status == "published")
        .options(joinedload(Post.author), joinedload(Post.tags), joinedload(Post.category))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    if current_user:
        post_ids = [post.id for post in posts]
        liked_ids = set()
        bookmarked_ids = set()
        if post_ids:
            liked_ids = {
                row[0]
                for row in db.query(PostLike.post_id)
                .filter(PostLike.user_id == current_user.id, PostLike.post_id.in_(post_ids))
                .all()
            }
            bookmarked_ids = {
                row[0]
                for row in db.query(PostBookmark.post_id)
                .filter(PostBookmark.user_id == current_user.id, PostBookmark.post_id.in_(post_ids))
                .all()
            }
        for post in posts:
            post.is_liked = post.id in liked_ids
            post.is_bookmarked = post.id in bookmarked_ids
    else:
        for post in posts:
            post.is_liked = False
            post.is_bookmarked = False
    return posts


@router.get("/month/{month}", response_model=List[PostResponse])
def posts_by_month(
    month: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    dialect = db.bind.dialect.name
    if dialect == "sqlite":
        month_key = func.strftime("%Y-%m", Post.created_at)
    else:
        month_key = func.to_char(Post.created_at, "YYYY-MM")

    posts = (
        db.query(Post)
        .filter(month_key == month, Post.status == "published")
        .options(joinedload(Post.author), joinedload(Post.tags), joinedload(Post.category))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    if current_user:
        post_ids = [post.id for post in posts]
        liked_ids = set()
        bookmarked_ids = set()
        if post_ids:
            liked_ids = {
                row[0]
                for row in db.query(PostLike.post_id)
                .filter(PostLike.user_id == current_user.id, PostLike.post_id.in_(post_ids))
                .all()
            }
            bookmarked_ids = {
                row[0]
                for row in db.query(PostBookmark.post_id)
                .filter(PostBookmark.user_id == current_user.id, PostBookmark.post_id.in_(post_ids))
                .all()
            }
        for post in posts:
            post.is_liked = post.id in liked_ids
            post.is_bookmarked = post.id in bookmarked_ids
    else:
        for post in posts:
            post.is_liked = False
            post.is_bookmarked = False
    return posts

@router.get("/user/{user_id}", response_model=List[PostResponse])
def get_user_posts(
    user_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id)
        .options(joinedload(Post.author), joinedload(Post.tags), joinedload(Post.category))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    if current_user:
        post_ids = [post.id for post in posts]
        liked_ids = set()
        bookmarked_ids = set()
        if post_ids:
            liked_ids = {
                row[0]
                for row in db.query(PostLike.post_id)
                .filter(PostLike.user_id == current_user.id, PostLike.post_id.in_(post_ids))
                .all()
            }
            bookmarked_ids = {
                row[0]
                for row in db.query(PostBookmark.post_id)
                .filter(PostBookmark.user_id == current_user.id, PostBookmark.post_id.in_(post_ids))
                .all()
            }
        for post in posts:
            post.is_liked = post.id in liked_ids
            post.is_bookmarked = post.id in bookmarked_ids
    else:
        for post in posts:
            post.is_liked = False
            post.is_bookmarked = False
    return posts

@router.get("/user/{user_id}/comments", response_model=List[CommentResponse])
def get_user_comments(
    user_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    comments = (
        db.query(Comment)
        .filter(Comment.author_id == user_id)
        .options(joinedload(Comment.author), joinedload(Comment.post))
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments

@router.post("/", response_model=PostResponse)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: PostCreate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    post = Post(
        title=post_in.title,
        content=post_in.content,
        cover_image=post_in.cover_image,
        author_id=current_user.id,
        category_id=post_in.category_id,
        status=post_in.status
    )

    tag_names = [t.strip() for t in (post_in.tags or []) if t and t.strip()]
    if tag_names:
        existing_tags = db.query(Tag).filter(Tag.name.in_(tag_names)).all()
        existing_by_name = {t.name: t for t in existing_tags}
        for name in tag_names:
            tag = existing_by_name.get(name)
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                db.flush()
            post.tags.append(tag)

    db.add(post)
    db.commit()
    db.refresh(post)
    post = db.query(Post).options(joinedload(Post.author), joinedload(Post.tags), joinedload(Post.category)).filter(Post.id == post.id).first()
    post.is_liked = False
    return post

@router.get("/{id}", response_model=PostDetailResponse)
def read_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    post = db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.tags),
        joinedload(Post.category),
        joinedload(Post.comments).joinedload(Comment.author)
    ).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    if post.status != "published":
        is_admin = current_user and current_user.role and current_user.role.name == "admin"
        is_author = current_user and current_user.id == post.author_id
        if not is_admin and not is_author:
            raise HTTPException(status_code=404, detail="文章不存在或未发布")

    if current_user:
        post.is_liked = (
            db.query(PostLike)
            .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
            .first()
            is not None
        )
        post.is_bookmarked = (
            db.query(PostBookmark)
            .filter(PostBookmark.post_id == post.id, PostBookmark.user_id == current_user.id)
            .first()
            is not None
        )
    else:
        post.is_liked = False
        post.is_bookmarked = False
    post.views += 1
    db.commit()
    db.refresh(post)
    return post

@router.post("/{id}/like")
async def like_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
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

@router.delete("/{id}/like")
async def unlike_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
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
    return {"likes_count": post.likes, "is_liked": False}

@router.post("/{id}/bookmark")
async def bookmark_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    existing_bookmark = db.query(PostBookmark).filter(
        PostBookmark.post_id == id,
        PostBookmark.user_id == current_user.id
    ).first()

    if existing_bookmark:
        db.delete(existing_bookmark)
        db.commit()
        return {"is_bookmarked": False}
    else:
        new_bookmark = PostBookmark(user_id=current_user.id, post_id=id)
        db.add(new_bookmark)
        db.commit()
        return {"is_bookmarked": True}

@router.delete("/{id}")
async def delete_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    is_admin = current_user.role and current_user.role.name == "admin"
    if post.author_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="无权限删除此文章")

    db.delete(post)
    db.commit()
    return {"message": "文章已删除"}

@router.delete("/comments/{id}")
async def delete_comment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    comment = db.query(Comment).filter(Comment.id == id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    is_admin = current_user.role and current_user.role.name == "admin"
    if comment.author_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="无权限删除此评论")

    db.delete(comment)
    db.commit()
    return {"message": "评论已删除"}

@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_user_required),
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
