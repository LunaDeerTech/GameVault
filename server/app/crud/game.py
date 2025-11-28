"""CRUD operations for Game model"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate


def get_game(db: Session, game_id: int) -> Optional[Game]:
    """Get game by ID"""
    # TODO: Implement get game by ID
    pass


def get_games(db: Session, skip: int = 0, limit: int = 100) -> List[Game]:
    """Get list of games"""
    # TODO: Implement get games
    pass


def get_game_by_name(db: Session, name: str) -> Optional[Game]:
    """Get game by name"""
    # TODO: Implement get game by name
    pass


def create_game(db: Session, game: GameCreate) -> Game:
    """Create new game"""
    # TODO: Implement create game
    pass


def update_game(db: Session, game_id: int, game_update: GameUpdate) -> Optional[Game]:
    """Update game"""
    # TODO: Implement update game
    pass


def delete_game(db: Session, game_id: int) -> bool:
    """Delete game"""
    # TODO: Implement delete game
    pass
