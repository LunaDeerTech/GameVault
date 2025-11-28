"""Content rating database model and initialization"""
from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base, SessionLocal


class ContentRating(Base):
    """Content rating model"""
    __tablename__ = "content_ratings"
    
    age_limit = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)


def init_default_content_ratings():
    """Initialize default content ratings if they don't exist"""
    db = SessionLocal()
    try:
        # Check if content ratings already exist
        existing_count = db.query(ContentRating).count()
        if existing_count > 0:
            return
        
        # Default content ratings based on common rating systems
        default_ratings = [
            ContentRating(
                age_limit=0,
                name="E - Everyone",
                description="Content is generally suitable for all ages"
            ),
            ContentRating(
                age_limit=3,
                name="EC - Early Childhood",
                description="Content is intended for young children"
            ),
            ContentRating(
                age_limit=7,
                name="E7+ - Everyone 7+",
                description="Content may contain mild cartoon, fantasy or mild violence"
            ),
            ContentRating(
                age_limit=10,
                name="E10+ - Everyone 10+",
                description="Content may contain more cartoon, fantasy or mild violence, mild language and/or minimal suggestive themes"
            ),
            ContentRating(
                age_limit=12,
                name="T - Teen (PEGI 12)",
                description="Content may contain violence, suggestive themes, crude humor, minimal blood, simulated gambling and/or infrequent use of strong language"
            ),
            ContentRating(
                age_limit=13,
                name="T - Teen",
                description="Content is generally suitable for ages 13 and up"
            ),
            ContentRating(
                age_limit=16,
                name="M16+ - Mature 16+",
                description="Content may contain intense violence, blood and gore, sexual content and/or strong language"
            ),
            ContentRating(
                age_limit=17,
                name="M - Mature 17+",
                description="Content is generally suitable for ages 17 and up. May contain intense violence, blood and gore, sexual content and/or strong language"
            ),
            ContentRating(
                age_limit=18,
                name="AO - Adults Only",
                description="Content suitable only for adults ages 18 and up. May include prolonged scenes of intense violence, graphic sexual content and/or gambling with real currency"
            ),
            ContentRating(
                age_limit=999,
                name="SL - Strictly Limited",
                description="Content is strictly limited to specific regions or audiences"
            )
        ]
        
        # Add all default ratings
        db.bulk_save_objects(default_ratings)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
