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
    db = SessionLocal()
    try:
        # Check if any admin users already exist
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            return
        
        # Generate a random password (12 characters with letters, digits, and punctuation)
        random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        logger.info("Creating default admin user...")
        logger.info("========== DEFAULT ADMIN CREDENTIALS ==========")
        logger.info("Username: admin")
        logger.info(f"Password: {random_password}")
        logger.info("===============================================")
        logger.warning("Default admin credentials should be changed immediately after first login.")
        
        
        # Create default admin user
        default_admin = User(
            username="admin",
            hashed_password=get_password_hash(random_password),
            is_admin=True
        )
        db.add(default_admin)
        db.commit()
    finally:
        db.close()