"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and default data"""
    import logging
    from app.models import game, user, save, playtime, content_rating
    from app.models.content_rating import init_default_content_ratings
    
    logger = logging.getLogger(__name__)
    
    # Check environment mode
    if settings.ENVIRONMENT == "development":
        # Development mode: Use direct table creation
        logger.info("Development mode: Creating tables directly...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    else:
        # Production mode: Use Alembic migrations
        logger.info("Production mode: Running Alembic migrations...")
        from app.core.migration import auto_migrate
        
        success = auto_migrate(backup=True)
        if not success:
            logger.error("Database migration failed! Application may not work correctly.")
            raise RuntimeError("Database migration failed")
        logger.info("Database migration completed")
    
    # Initialize default content ratings
    try:
        logger.info("Initializing default content ratings...")
        init_default_content_ratings()
        logger.info("Default content ratings initialized")
    except Exception as e:
        logger.error(f"Failed to initialize content ratings: {e}")
        raise
