"""CRUD operations for User model"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    # TODO: Implement get user by ID
    pass


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    # TODO: Implement get user by email
    pass


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    # TODO: Implement get user by username
    pass


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users"""
    # TODO: Implement get users
    pass


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user"""
    # TODO: Implement create user
    pass


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    # TODO: Implement update user
    pass


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    # TODO: Implement delete user
    pass
