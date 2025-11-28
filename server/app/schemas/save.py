"""Game save Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GameSaveBase(BaseModel):
    """Base game save schema"""
    # TODO: Define base save fields
    pass


class GameSaveCreate(GameSaveBase):
    """Schema for creating a game save"""
    # TODO: Define fields for save creation
    pass


class GameSave(GameSaveBase):
    """Schema for game save response"""
    # TODO: Define fields for save response
    
    class Config:
        from_attributes = True
