from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

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
    post: Optional["PostResponse"] = None

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    cover_image: Optional[str] = None
    status: str = "published"
    category_id: Optional[int] = None

class PostCreate(PostBase):
    tags: List[str] = []

class PostResponse(PostBase):
    id: int
    author_id: int
    views: int
    likes: int
    created_at: datetime
    author: UserResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    is_liked: bool = False
    is_bookmarked: bool = False

    class Config:
        from_attributes = True

class PostDetailResponse(PostResponse):
    comments: List[CommentResponse] = []
