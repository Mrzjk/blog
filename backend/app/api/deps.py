from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import TokenPayload
from typing import Optional
from datetime import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    if token is None:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    
    if user:
        now = datetime.utcnow()
        if not user.is_active and user.banned_until and user.banned_until <= now:
            user.is_active = True
            user.banned_until = None
            db.commit()
            
        if user.is_muted and user.muted_until and user.muted_until <= now:
            user.is_muted = False
            user.muted_until = None
            db.commit()
            
    return user

def get_current_user_required(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if user is None:
        raise credentials_exception
        
    now = datetime.utcnow()
    # Check ban status
    if not user.is_active:
        if user.banned_until and user.banned_until <= now:
            user.is_active = True
            user.banned_until = None
            db.commit()
        else:
            raise HTTPException(status_code=403, detail="您的账号已被封禁")
            
    # Check mute status
    if user.is_muted:
        if user.muted_until and user.muted_until <= now:
            user.is_muted = False
            user.muted_until = None
            db.commit()
            
    return user

async def get_current_user_ws(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    return user