from pydantic import BaseModel
from typing import Optional

class FriendRequestCreate(BaseModel):
    friend_id: int

class FriendshipResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int
    status: str

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    sender_id: Optional[int]
    type: str
    content: Optional[str]
    is_read: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True