import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Dict, Any

from app.database import get_db
from app.api.deps import get_current_user, get_current_user_required
from app.models.user import User
from app.models.post import Post
from app.models.social import Notification
from app.models.setting import SystemSetting
from app.schemas.admin import DashboardStats, SystemSettingsUpdate, AnnouncementCreate

router = APIRouter()

def check_admin(current_user: User = Depends(get_current_user_required)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(check_admin)):
    total_users = db.query(User).count()
    total_posts = db.query(Post).count()
    
    today = date.today()
    new_users_today = db.query(User).filter(User.created_at >= today).count()
    
    # Assuming 'draft' is the status for pending review, or you can use 'pending'
    pending_review_posts = db.query(Post).filter(Post.status == "draft").count()
    
    return DashboardStats(
        total_users=total_users,
        total_posts=total_posts,
        new_users_today=new_users_today,
        pending_review_posts=pending_review_posts
    )

@router.get("/settings", response_model=Dict[str, Any])
def get_system_settings(db: Session = Depends(get_db), current_user: User = Depends(check_admin)):
    settings_db = db.query(SystemSetting).all()
    settings_dict = {}
    for s in settings_db:
        try:
            settings_dict[s.key] = json.loads(s.value)
        except json.JSONDecodeError:
            settings_dict[s.key] = s.value
            
    # Default settings if none exist
    default_settings = {
        "siteName": "Blog System",
        "allowRegister": True,
        "requireReview": True
    }
    
    for k, v in default_settings.items():
        if k not in settings_dict:
            settings_dict[k] = v
            
    return settings_dict

@router.put("/settings")
def update_system_settings(
    data: SystemSettingsUpdate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin)
):
    for key, value in data.settings.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        value_str = json.dumps(value)
        if setting:
            setting.value = value_str
        else:
            new_setting = SystemSetting(key=key, value=value_str)
            db.add(new_setting)
            
    db.commit()
    return {"message": "Settings updated successfully"}

@router.post("/announcements")
def publish_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    users = db.query(User).all()
    notifications = []
    
    content_preview = data.title + " - " + data.content
    if len(content_preview) > 250:
        content_preview = content_preview[:247] + "..."
        
    for user in users:
        notifications.append(Notification(
            user_id=user.id,
            sender_id=current_user.id,
            type="system_announcement",
            content=content_preview
        ))
        
    db.bulk_save_objects(notifications)
    db.commit()
    
    return {"message": "Announcement published successfully"}
