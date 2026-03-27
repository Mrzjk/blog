from pydantic import BaseModel
from typing import Dict, Any, Optional

class DashboardStats(BaseModel):
    total_users: int
    total_posts: int
    new_users_today: int
    pending_review_posts: int

class SystemSettingsUpdate(BaseModel):
    settings: Dict[str, Any]

class AnnouncementCreate(BaseModel):
    title: str
    content: str
