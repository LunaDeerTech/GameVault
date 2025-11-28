"""Game Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class GameBase(BaseModel):
    """Base game schema with common fields shared by create/update/response schemas.

    Keep fields minimal here; extend in Game / GameCreate / GameUpdate as needed.
    """
    title: Optional[str] = None
    slug: str   # read from game file path
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None

    platforms: Optional[List[str]] = None  # e.g. ["Windows", "Linux"]
    tags: Optional[List[str]] = None
    content_rating_age_limit : Optional[int] = None

    steam_id: Optional[int] = None
    igdb_id: Optional[int] = None

    # Paths are stored relative to configured /storage root where possible
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    intro_images: Optional[List[str]] = None

    # Manifest / integrity metadata (used for incremental updates)
    size_bytes: Optional[int] = None
    manifest_hash: Optional[str] = None  # SHA-256 of manifest.json


class GameCreate(GameBase):
    """Schema for creating a game
        
    All fields are inherited from GameBase. Title is required, others optional.
    """
    slug: str  # required for creation


class GameUpdate(BaseModel):
    """Schema for updating a game
    
    All fields are optional to support partial updates (PATCH).
    """
    title: Optional[str] = None
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None
    
    platforms: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    content_rating_age_limit : Optional[int] = None
    
    steam_id: Optional[int] = None
    igdb_id: Optional[int] = None
    
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    intro_images: Optional[List[str]] = None
    
    size_bytes: Optional[int] = None
    manifest_hash: Optional[str] = None  # SHA-256 of manifest.json


class Game(GameBase):
    """Schema for game response (reading data)"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    manifest_path: Optional[str] = None  # path to manifest.json


