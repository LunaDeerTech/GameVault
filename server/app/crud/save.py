"""CRUD operations for GameSave model"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.save import GameSave
from app.schemas.save import GameSaveCreate


def get_save(db: Session, save_id: int) -> Optional[GameSave]:
    """Get save by ID"""
    return db.query(GameSave).filter(GameSave.id == save_id).first()


def get_save_by_id_and_user(db: Session, save_id: int, user_id: int) -> Optional[GameSave]:
    """Get save by ID and user ID (for permission check)"""
    return db.query(GameSave).filter(
        GameSave.id == save_id,
        GameSave.user_id == user_id
    ).first()


def get_game_saves(db: Session, game_id: int, user_id: int) -> List[GameSave]:
    """Get all saves for a game and user"""
    return db.query(GameSave).filter(
        GameSave.game_id == game_id,
        GameSave.user_id == user_id
    ).order_by(GameSave.created_at.desc()).all()


def get_user_saves(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[GameSave]:
    """Get all saves for a user with pagination"""
    return db.query(GameSave).filter(
        GameSave.user_id == user_id
    ).order_by(GameSave.created_at.desc()).offset(skip).limit(limit).all()


def get_saves_by_file_path(db: Session, file_path: str, user_id: int) -> Optional[GameSave]:
    """Get save by file path and user ID (to avoid duplicates)"""
    return db.query(GameSave).filter(
        GameSave.file_path == file_path,
        GameSave.user_id == user_id
    ).first()


def create_save(db: Session, save: GameSaveCreate) -> GameSave:
    """Create new save"""
    db_save = GameSave(
        user_id=save.user_id,
        game_id=save.game_id,
        file_path=save.file_path,
        file_size=save.file_size
    )
    db.add(db_save)
    db.commit()
    db.refresh(db_save)
    return db_save


def delete_save(db: Session, save_id: int, user_id: int) -> bool:
    """Delete save (with user permission check)"""
    db_save = db.query(GameSave).filter(
        GameSave.id == save_id,
        GameSave.user_id == user_id
    ).first()
    if db_save:
        db.delete(db_save)
        db.commit()
        return True
    return False


def delete_saves_by_game(db: Session, game_id: int, user_id: int) -> int:
    """Delete all saves for a game and user, returns count of deleted saves"""
    deleted_count = db.query(GameSave).filter(
        GameSave.game_id == game_id,
        GameSave.user_id == user_id
    ).delete()
    db.commit()
    return deleted_count


def count_user_saves(db: Session, user_id: int) -> int:
    """Count total saves for a user"""
    return db.query(GameSave).filter(GameSave.user_id == user_id).count()
