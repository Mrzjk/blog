from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    cover_image = Column(String(255), nullable=True)
    url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True) # 上线/下线
    created_at = Column(DateTime, default=datetime.utcnow)

    histories = relationship("UserGameHistory", back_populates="game")

class UserGameHistory(Base):
    __tablename__ = "user_game_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    game_id = Column(Integer, ForeignKey("games.id"), index=True)
    score = Column(Integer, default=0) # 分数/战绩
    duration = Column(Integer, default=0) # 时长(秒)
    played_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="histories")
    user = relationship("User")
