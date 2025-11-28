"""Game play time database model"""
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class GamePlaytime(Base):
    """Game play time model"""
    __tablename__ = "game_play_time"
    
    id = Column(Integer, primary_key=True, index=True)
    
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    play_time_minutes = Column(Integer, default=0)
    
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
