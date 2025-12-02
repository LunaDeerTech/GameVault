"""Game database model"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func

from app.core.database import Base


class Game(Base):
    """Game model"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(255), nullable=False, index=True)
    path = Column(String(255), nullable=False, unique=True)
    
    description = Column(Text, nullable=True)
    developer = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    release_date = Column(String(50), nullable=True)
    
    steam_id = Column(String(50), nullable=True, index=True)
    igdb_id = Column(String(50), nullable=True, index=True)
    
    cover_image = Column(String(512), nullable=True)
    banner_image = Column(String(512), nullable=True)
    intro_images = Column(Text, nullable=True)  # JSON-encoded list of image paths
    platforms = Column(Text, nullable=True)  # JSON-encoded list of platforms
    content_rating_age_limit = Column(Integer, ForeignKey("content_ratings.age_limit"), nullable=True)
    
    total_size = Column(BigInteger, default=0)
    manifest_hash = Column(String(64), nullable=True)
    
    indexing_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

