from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.post import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter()

@router.get("/", response_model=Any)
def read_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    from sqlalchemy import func
    from app.models.post import Post
    
    rows = (
        db.query(Category, func.count(Post.id))
        .outerjoin(Post, Category.id == Post.category_id)
        .group_by(Category.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for cat, count in rows:
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "created_at": cat.created_at,
            "count": count
        }
        result.append(cat_dict)
        
    return result

@router.post("/", response_model=CategoryResponse)
def create_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    category = db.query(Category).filter(Category.name == category_in.name).first()
    if category:
        raise HTTPException(status_code=400, detail="分类已存在")
        
    category = Category(
        name=category_in.name,
        description=category_in.description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.put("/{id}", response_model=CategoryResponse)
def update_category(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
        
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
        
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
        
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{id}")
def delete_category(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
        
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
        
    db.delete(category)
    db.commit()
    return {"message": "分类已删除"}
