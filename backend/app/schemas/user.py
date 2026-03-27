from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)
    bio: Optional[str] = Field(default=None, max_length=255)
    avatar: Optional[str] = None
    birthday: Optional[datetime] = None

class UserCreate(UserBase):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=64)

class UserUpdate(UserBase):
    password: Optional[str] = Field(default=None, min_length=6, max_length=64)
    exp: Optional[int] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: Optional[str] = None

    class Config:
        from_attributes = True

class UserInDBBase(UserBase):
    id: int
    level: int
    exp: int
    role_id: int
    is_active: bool
    is_muted: Optional[bool] = False
    muted_until: Optional[datetime] = None
    banned_until: Optional[datetime] = None
    created_at: datetime
    last_active: Optional[datetime] = None
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class PaginatedUserResponse(BaseModel):
    total: int
    items: List[UserResponse]
