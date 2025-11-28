"""CRUD operations for GameSave model"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.save import GameSave
from app.schemas.save import GameSaveCreate


def get_save(db: Session, save_id: int) -> Optional[GameSave]:
    """Get save by ID"""
    # TODO: Implement get save by ID
    pass


def get_game_saves(db: Session, game_id: int, user_id: int) -> List[GameSave]:
    """Get all saves for a game and user"""
    # TODO: Implement get game saves
    pass


def create_save(db: Session, save: GameSaveCreate, user_id: int) -> GameSave:
    """Create new save"""
    # TODO: Implement create save
    pass


def delete_save(db: Session, save_id: int) -> bool:
    """Delete save"""
    # TODO: Implement delete save
    pass
