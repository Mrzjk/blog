from datetime import datetime, timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate

router = APIRouter()

def calculate_exp_for_level(level: int) -> int:
    return 10 * (2 ** (max(1, level) - 1))

def total_exp_needed_for_next_level(level: int) -> int:
    return sum(calculate_exp_for_level(l) for l in range(1, max(1, level) + 1))

def apply_level_up(user: User) -> None:
    while user.exp >= total_exp_needed_for_next_level(user.level):
        user.level += 1

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    login_value = form_data.username.strip()
    user = db.query(User).filter(
        or_(User.username == login_value, User.email == login_value)
    ).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名/邮箱或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="账号已被禁用")

    user.last_active = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    user = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="邮箱已被注册",
        )
    user = db.query(User).filter(User.username == user_in.username.strip()).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在",
        )

    role = db.query(Role).filter(Role.name == "user").first()
    if not role:
        role = Role(name="user", permissions="")
        db.add(role)
        db.commit()
        db.refresh(role)

    user = User(
        email=user_in.email.strip().lower(),
        username=user_in.username.strip(),
        hashed_password=security.get_password_hash(user_in.password),
        role_id=role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if user_in.email and user_in.email != current_user.email:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    if user_in.username and user_in.username != current_user.username:
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(status_code=400, detail="用户名已被使用")

    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        current_user.hashed_password = hashed_password
        del update_data["password"]
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    user_with_role = db.query(User).options(joinedload(User.role)).filter(User.id == current_user.id).first()
    return user_with_role

@router.post("/heartbeat")
def heartbeat(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    user = db.query(User).filter(User.id == current_user.id).first()
    now = datetime.utcnow()

    if not user.last_active:
        user.last_active = now
        db.commit()
        db.refresh(user)
        return {
            "exp": user.exp,
            "level": user.level,
            "exp_for_next_level": calculate_exp_for_level(user.level)
        }

    minutes_passed = (now - user.last_active).total_seconds() / 60
    gained = int(minutes_passed // 10)
    if gained > 0:
        user.exp += gained
        user.last_active = user.last_active + timedelta(minutes=gained * 10)
        apply_level_up(user)
    db.commit()
    db.refresh(user)
    return {
        "exp": user.exp,
        "level": user.level,
        "exp_for_next_level": calculate_exp_for_level(user.level)
    }

@router.get("/user/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.get("/", response_model=List[UserResponse])
def search_users(
    q: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    users = db.query(User).filter(
        User.username.contains(q)
    ).offset(skip).limit(limit).all()
    return users

@router.get("/users")
def list_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    is_admin = current_user.role and current_user.role.name == "admin"
    if not is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/ban")
def ban_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    is_admin = current_user.role and current_user.role.name == "admin"
    if not is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if target_user.role and target_user.role.name == "admin":
        raise HTTPException(status_code=400, detail="无法封禁管理员")

    target_user.is_active = False
    db.commit()
    return {"message": f"用户 {target_user.username} 已被封禁"}

@router.put("/users/{user_id}/unban")
def unban_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    is_admin = current_user.role and current_user.role.name == "admin"
    if not is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    target_user.is_active = True
    db.commit()
    return {"message": f"用户 {target_user.username} 已解封"}
