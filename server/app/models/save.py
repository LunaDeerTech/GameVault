"""Game save database model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GameSave(Base):
    """Game save model"""
    __tablename__ = "game_saves"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
