"""Game save Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GameSaveBase(BaseModel):
    """Base game save schema"""
    file_path: str = Field(..., description="Path to the save file", max_length=512)
    file_size: int = Field(default=0, description="Size of the save file in bytes", ge=0)


class GameSaveCreate(GameSaveBase):
    """Schema for creating a game save"""
    user_id: int = Field(..., description="ID of the user who owns this save", gt=0)
    game_id: int = Field(..., description="ID of the game this save belongs to", gt=0)


class GameSave(GameSaveBase):
    """Schema for game save response"""
    id: int = Field(..., description="Unique identifier for the save")
    user_id: int = Field(..., description="ID of the user who owns this save")
    game_id: int = Field(..., description="ID of the game this save belongs to")
    created_at: datetime = Field(..., description="When the save was created")
    
    class Config:
        from_attributes = True


class GameSaveList(BaseModel):
    """Schema for listing game saves"""
    saves: list[GameSave] = Field(default=[], description="List of game saves")
    total: int = Field(..., description="Total number of saves", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    pages: int = Field(..., description="Total number of pages", ge=1)
