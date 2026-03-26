from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.api import deps
from app.models.game import Game, UserGameHistory
from app.models.user import User
from app.schemas.game import GameCreate, GameResponse, GameUpdate, GameHistoryCreate, GameHistoryResponse

router = APIRouter()

def get_current_user_optional(db: Session = Depends(deps.get_db), token: str = Depends(deps.oauth2_scheme)) -> Optional[User]:
    return deps.get_current_user(db, token)

@router.get("/", response_model=List[GameResponse])
def read_games(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    query = db.query(Game)
    if not current_user or (current_user.role and current_user.role.name != "admin"):
        query = query.filter(Game.is_active == True)
    games = query.offset(skip).limit(limit).all()
    return games

@router.post("/", response_model=GameResponse)
def create_game(
    *,
    db: Session = Depends(deps.get_db),
    game_in: GameCreate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    game = Game(
        name=game_in.name,
        description=game_in.description,
        cover_image=game_in.cover_image,
        url=game_in.url,
        is_active=game_in.is_active
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@router.put("/{id}", response_model=GameResponse)
def update_game(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    game_in: GameUpdate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
        
    game = db.query(Game).filter(Game.id == id).first()
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
        
    update_data = game_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)
        
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@router.post("/history", response_model=GameHistoryResponse)
def record_game_history(
    *,
    db: Session = Depends(deps.get_db),
    history_in: GameHistoryCreate,
    current_user: User = Depends(deps.get_current_user_required),
) -> Any:
    game = db.query(Game).filter(Game.id == history_in.game_id).first()
    if not game or not game.is_active:
        raise HTTPException(status_code=404, detail="游戏不可用")
        
    history = UserGameHistory(
        user_id=current_user.id,
        game_id=history_in.game_id,
        score=history_in.score,
        duration=history_in.duration
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

@router.get("/history/user/{user_id}", response_model=List[GameHistoryResponse])
def get_user_game_history(
    user_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    histories = (
        db.query(UserGameHistory)
        .filter(UserGameHistory.user_id == user_id)
        .options(joinedload(UserGameHistory.game))
        .order_by(UserGameHistory.played_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return histories
