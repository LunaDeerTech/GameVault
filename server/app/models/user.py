"""User database model"""
import logging
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.database import Base, SessionLocal
from app.core.security import get_password_hash
import secrets
import string

logger = logging.getLogger(__name__)

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
        
    email = Column(String(255), unique=True, index=True, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def init_default_admin_user():
    """Initialize a default admin user if none exist"""
    from app.crud.user import get_admin_users, create_user
    from app.schemas.user import UserCreate
    
    db = SessionLocal()
    try:
        # Check if any admin users already exist
        existing_admins = get_admin_users(db, limit=1)
        if existing_admins:
            return
        
        # Generate a random password (12 characters with letters, digits, and punctuation)
        random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        logger.info("Creating default admin user...")
        logger.info("========== DEFAULT ADMIN CREDENTIALS ==========")
        logger.info("Username: admin")
        logger.info(f"Password: {random_password}")
        logger.info("===============================================")
        logger.warning("Default admin credentials should be changed immediately after first login.")
        
        # Create default admin user using schema and CRUD
        admin_user_data = UserCreate(
            username="admin",
            password=random_password,
            is_admin=True,
            is_active=True
        )
        create_user(db, admin_user_data)
        logger.info("Default admin user created successfully.")
        
    except Exception as e:
        logger.error(f"Error creating default admin user: {e}")
        db.rollback()
    finally:
        db.close()