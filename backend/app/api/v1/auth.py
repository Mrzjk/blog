from datetime import datetime, timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate

router = APIRouter()

def calculate_exp_for_level(level: int) -> int:
    return 10 * (2 ** (level - 1))

def check_level_up(user: User) -> bool:
    total_exp_needed = sum(calculate_exp_for_level(l) for l in range(1, user.level + 1))
    if user.exp >= total_exp_needed:
        user.level += 1
        return True
    return False

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
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    user = db.query(User).filter(User.id == current_user.id).first()

    if user_in.email is not None:
        email_exists = db.query(User).filter(
            User.email == user_in.email.strip().lower(),
            User.id != current_user.id
        ).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        user.email = user_in.email.strip().lower()
    if user_in.username is not None:
        username_exists = db.query(User).filter(
            User.username == user_in.username.strip(),
            User.id != current_user.id
        ).first()
        if username_exists:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = user_in.username.strip()
    if user_in.bio is not None:
        user.bio = user_in.bio.strip()
    if user_in.avatar is not None:
        user.avatar = user_in.avatar
    if user_in.password is not None:
        user.hashed_password = security.get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)
    return user

@router.post("/heartbeat")
def heartbeat(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    user = db.query(User).filter(User.id == current_user.id).first()
    now = datetime.utcnow()

    if user.last_active:
        minutes_passed = (now - user.last_active).total_seconds() / 60
        if minutes_passed >= 10:
            user.exp += 1
            check_level_up(user)

    user.last_active = now
    db.commit()
    db.refresh(user)
    return {
        "exp": user.exp,
        "level": user.level,
        "exp_for_next_level": calculate_exp_for_level(user.level)
    }

@router.get("/{user_id}", response_model=UserResponse)
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
