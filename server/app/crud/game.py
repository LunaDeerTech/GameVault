"""CRUD operations for Game model"""
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate


def get_game(db: Session, game_id: int) -> Optional[Game]:
    """Get game by ID"""
    return db.query(Game).filter(Game.id == game_id).first()


def get_games(db: Session, skip: int = 0, limit: int = 100) -> List[Game]:
    """Get list of games with pagination"""
    return db.query(Game).offset(skip).limit(limit).all()


def get_game_by_name(db: Session, name: str) -> Optional[Game]:
    """Get game by exact name match"""
    return db.query(Game).filter(Game.name == name).first()


def get_game_by_folder_name(db: Session, folder_name: str) -> Optional[Game]:
    """Get game by folder name (slug)"""
    return db.query(Game).filter(Game.folder_name == folder_name).first()


def get_games_by_steam_id(db: Session, steam_id: str) -> Optional[Game]:
    """Get game by Steam ID"""
    return db.query(Game).filter(Game.steam_id == steam_id).first()


def get_games_by_igdb_id(db: Session, igdb_id: str) -> Optional[Game]:
    """Get game by IGDB ID"""
    return db.query(Game).filter(Game.igdb_id == igdb_id).first()


def search_games(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Game]:
    """Search games by name, developer, or publisher"""
    search_filter = or_(
        Game.name.ilike(f"%{query}%"),
        Game.developer.ilike(f"%{query}%"),
        Game.publisher.ilike(f"%{query}%")
    )
    return db.query(Game).filter(search_filter).offset(skip).limit(limit).all()


def create_game(db: Session, game: GameCreate) -> Game:
    """Create new game"""
    # Convert schema to model data
    game_data = game.dict(exclude_unset=True)
    
    # Handle special fields that need conversion
    if hasattr(game, 'platforms') and game.platforms:
        game_data['platforms'] = json.dumps(game.platforms)
    if hasattr(game, 'intro_images') and game.intro_images:
        game_data['intro_images'] = json.dumps(game.intro_images)
    
    # Map schema fields to model fields
    model_data = {
        'name': game_data.get('title') or game_data.get('slug'),
        'folder_name': game_data.get('slug'),
        'description': game_data.get('description'),
        'developer': game_data.get('developer'),
        'publisher': game_data.get('publisher'),
        'release_date': str(game_data.get('release_date')) if game_data.get('release_date') else None,
        'steam_id': str(game_data.get('steam_id')) if game_data.get('steam_id') else None,
        'igdb_id': str(game_data.get('igdb_id')) if game_data.get('igdb_id') else None,
        'cover_image': game_data.get('cover_image'),
        'banner_image': game_data.get('banner_image'),
        'intro_images': game_data.get('intro_images'),
        'platforms': game_data.get('platforms'),
        'content_rating_age_limit': game_data.get('content_rating_age_limit'),
        'total_size': game_data.get('size_bytes', 0),
        'manifest_hash': game_data.get('manifest_hash'),
    }
    
    # Remove None values
    model_data = {k: v for k, v in model_data.items() if v is not None}
    
    db_game = Game(**model_data)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def update_game(db: Session, game_id: int, game_update: GameUpdate) -> Optional[Game]:
    """Update game"""
    db_game = get_game(db, game_id)
    if not db_game:
        return None
    
    update_data = game_update.dict(exclude_unset=True)
    
    # Handle special fields that need conversion
    if 'platforms' in update_data and update_data['platforms']:
        update_data['platforms'] = json.dumps(update_data['platforms'])
    if 'intro_images' in update_data and update_data['intro_images']:
        update_data['intro_images'] = json.dumps(update_data['intro_images'])
    
    # Map schema fields to model fields
    model_updates = {}
    if 'title' in update_data:
        model_updates['name'] = update_data['title']
    if 'slug' in update_data:
        model_updates['folder_name'] = update_data['slug']
    if 'description' in update_data:
        model_updates['description'] = update_data['description']
    if 'developer' in update_data:
        model_updates['developer'] = update_data['developer']
    if 'publisher' in update_data:
        model_updates['publisher'] = update_data['publisher']
    if 'release_date' in update_data:
        model_updates['release_date'] = str(update_data['release_date']) if update_data['release_date'] else None
    if 'steam_id' in update_data:
        model_updates['steam_id'] = str(update_data['steam_id']) if update_data['steam_id'] else None
    if 'igdb_id' in update_data:
        model_updates['igdb_id'] = str(update_data['igdb_id']) if update_data['igdb_id'] else None
    if 'cover_image' in update_data:
        model_updates['cover_image'] = update_data['cover_image']
    if 'banner_image' in update_data:
        model_updates['banner_image'] = update_data['banner_image']
    if 'intro_images' in update_data:
        model_updates['intro_images'] = update_data['intro_images']
    if 'platforms' in update_data:
        model_updates['platforms'] = update_data['platforms']
    if 'content_rating_age_limit' in update_data:
        model_updates['content_rating_age_limit'] = update_data['content_rating_age_limit']
    if 'size_bytes' in update_data:
        model_updates['total_size'] = update_data['size_bytes']
    if 'manifest_hash' in update_data:
        model_updates['manifest_hash'] = update_data['manifest_hash']
    if 'scraped_at' in update_data:
        model_updates['scraped_at'] = update_data['scraped_at']
    
    # Update the game
    for key, value in model_updates.items():
        setattr(db_game, key, value)
    
    db.commit()
    db.refresh(db_game)
    return db_game


def delete_game(db: Session, game_id: int) -> bool:
    """Delete game"""
    db_game = get_game(db, game_id)
    if not db_game:
        return False
    
    db.delete(db_game)
    db.commit()
    return True


def get_games_count(db: Session) -> int:
    """Get total count of games"""
    return db.query(Game).count()


def get_games_by_developer(db: Session, developer: str, skip: int = 0, limit: int = 100) -> List[Game]:
    """Get games by developer"""
    return db.query(Game).filter(Game.developer == developer).offset(skip).limit(limit).all()


def get_games_by_tag(db: Session, tag: str, skip: int = 0, limit: int = 100) -> List[Game]:
    """Get games by tag"""
    tag_filter = f'%{tag}%'
    return db.query(Game).filter(Game.tags.ilike(tag_filter)).offset(skip).limit(limit).all()

def get_games_by_publisher(db: Session, publisher: str, skip: int = 0, limit: int = 100) -> List[Game]:
    """Get games by publisher"""
    return db.query(Game).filter(Game.publisher == publisher).offset(skip).limit(limit).all()


def update_game_manifest_hash(db: Session, game_id: int, manifest_hash: str) -> Optional[Game]:
    """Update only the manifest hash for a game"""
    db_game = get_game(db, game_id)
    if not db_game:
        return None
    
    db_game.manifest_hash = manifest_hash
    db.commit()
    db.refresh(db_game)
    return db_game


def update_game_size(db: Session, game_id: int, total_size: int) -> Optional[Game]:
    """Update only the total size for a game"""
    db_game = get_game(db, game_id)
    if not db_game:
        return None
    
    db_game.total_size = total_size
    db.commit()
    db.refresh(db_game)
    return db_game
