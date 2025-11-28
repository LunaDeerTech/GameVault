"""Game Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class GameBase(BaseModel):
    """Base game schema with common fields shared by create/update/response schemas.

    Keep fields minimal here; extend in Game / GameCreate / GameUpdate as needed.
    """
    title: Optional[str] = Field(None, description="Title of the game", max_length=200)
    slug: str = Field(..., description="Slug for the game, read from game file path")
    description: Optional[str] = Field(None, description="Description of the game")
    developer: Optional[str] = Field(None, description="Developer of the game")
    publisher: Optional[str] = Field(None, description="Publisher of the game")
    release_date: Optional[datetime] = Field(None, description="Release date of the game")

    platforms: Optional[List[str]] = Field(None, description="List of platforms the game supports, e.g., ['Windows', 'Linux']")
    tags: Optional[List[str]] = Field(None, description="List of tags associated with the game")
    content_rating_age_limit : Optional[int] = Field(None, description="Content rating age limit for the game")
    
    steam_id: Optional[int] = Field(None, description="Steam ID of the game")
    igdb_id: Optional[int] = Field(None, description="IGDB ID of the game")

    # Paths are stored relative to configured /storage root where possible
    cover_image: Optional[str] = Field(None, description="Path to the cover image, relative to storage root")
    banner_image: Optional[str] = Field(None, description="Path to the banner image, relative to storage root")
    intro_images: Optional[List[str]] = Field(None, description="List of paths to intro images, relative to storage root")

    # Manifest / integrity metadata (used for incremental updates)
    size_bytes: Optional[int] = Field(None, description="Total size of the game files in bytes")
    manifest_hash: Optional[str] = Field(None, description="SHA-256 hash of manifest.json")

class GameCreate(GameBase):
    """Schema for creating a game
        
    All fields are inherited from GameBase. Title is required, others optional.
    """
    slug: str = Field(..., description="Slug for the game, read from game file path")


class GameUpdate(GameBase):
    """Schema for updating a game

    All fields are optional for partial updates.
    """
    pass


class Game(GameBase):
    """Schema for game response (reading data)"""
    id: int = Field(..., description="Unique identifier for the game")
    created_at: datetime = Field(..., description="Timestamp when the game was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the game was last updated")
    manifest_path: Optional[str] = Field(None, description="Path to manifest.json")
