from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse

class GameBase(BaseModel):
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    url: str
    is_active: bool = True

class GameCreate(GameBase):
    pass

class GameUpdate(GameBase):
    name: Optional[str] = None
    url: Optional[str] = None

class GameResponse(GameBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GameHistoryCreate(BaseModel):
    game_id: int
    score: int = 0
    duration: int = 0

class GameHistoryResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    score: int
    duration: int
    played_at: datetime
    game: GameResponse

    class Config:
        from_attributes = True
