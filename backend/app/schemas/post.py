from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse

class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    post_id: int

class CommentResponse(CommentBase):
    id: int
    post_id: int
    author_id: int
    likes: int
    created_at: datetime
    author: UserResponse

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    cover_image: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author_id: int
    views: int
    likes: int
    created_at: datetime
    author: UserResponse

    class Config:
        from_attributes = True

class PostDetailResponse(PostResponse):
    comments: List[CommentResponse] = []