from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.post import Tag
from app.models.user import User
from app.schemas.post import TagCreate, TagResponse, TagUpdate

router = APIRouter()

@router.get("/", response_model=Any)
def read_tags(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    from sqlalchemy import func
    from app.models.post import Post
    
    rows = (
        db.query(Tag, func.count(Post.id))
        .outerjoin(Tag.posts)
        .group_by(Tag.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for tag, count in rows:
        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "description": tag.description,
            "created_at": tag.created_at,
            "count": count
        }
        result.append(tag_dict)
        
    return result

@router.post("/", response_model=TagResponse)
def create_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag_in: TagCreate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    tag = db.query(Tag).filter(Tag.name == tag_in.name).first()
    if tag:
        raise HTTPException(status_code=400, detail="标签已存在")
        
    tag = Tag(
        name=tag_in.name,
        color=tag_in.color,
        description=tag_in.description
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.put("/{id}", response_model=TagResponse)
def update_tag(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    tag_in: TagUpdate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
        
    tag = db.query(Tag).filter(Tag.id == id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
        
    update_data = tag_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
        
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/{id}")
def delete_tag(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
        
    tag = db.query(Tag).filter(Tag.id == id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
        
    db.delete(tag)
    db.commit()
    return {"message": "标签已删除"}
