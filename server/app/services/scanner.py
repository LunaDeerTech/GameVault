"""Game directory scan service"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.manifest import ManifestService
from app.services.scraper import metadataScraperService
from app.crud.game import (
    get_game, 
    get_game_by_path,
    update_game,
    create_game, 
    update_game_manifest_hash,
    update_game_size
)
from app.schemas.game import GameCreate, GameUpdate
from app.core.database import SessionLocal
from app.models.game import Game


logger = logging.getLogger(__name__)


class ScannerService():
    """Base scanner service class"""
    
    def __init__(self, games_directory: Path):
        """
        Initialize watchdog service
        
        Args:
            games_directory: Path to the games directory to monitor
                e.g. /path/to/games
                        - Game1
                        - Game2
        """
        self.games_directory = games_directory
        
    async def start_scan(self):
        scan_tasks = []
        if self.games_directory.exists() and self.games_directory.is_dir():
            for item in self.games_directory.iterdir():
                if item.is_dir():
                    scan_tasks.append(asyncio.create_task(self.scan_game_directory(item)))
        else:
            raise ValueError(f"Games directory {self.games_directory} does not exist or is not a directory")
        await asyncio.gather(*scan_tasks)
        
    async def stop_scan(self):
        pass
        
    async def scan_game_directory(self, game_path: Path) -> None:
        if not game_path.exists() or not game_path.is_dir():
            logger.warning(f"Invalid game directory: {game_path}")
            return None
        
        logger.info(f"Scanning game directory: {game_path}")
        db = SessionLocal()
        
        # 1. Ensure game entry exists in DB
        game = await self.ensure_game_entry(db, game_path)
        if not game:
            logger.error(f"Failed to ensure game entry for path: {game_path}")
            return None
        # 2. Process manifest
        await self.process_manifest(db, game, game_path)
        # 3. process metadata scraping
        await self.process_metadata_scrape(db, game)
        
        logger.info(f"Completed scanning for game: {game.name}")
        
        # 4. Start Watchdog monitoring
        # TODO: Implement watchdog monitoring for game directory changes
        pass
            
    async def process_manifest(self, db: Session, game: Game, game_path: Path) -> Optional[Dict[str, Any]]:
        manifest_path = game_path / 'manifest.json'
        
        if not game.manifest_hash:
            # No manifest hash in DB, generate manifest
            return await self.generate_manifest_for_game(game, game_path, force=True, db=db)
        else:
            if manifest_path.exists():
                # Check if manifest hash matches
                manifest_hash = await ManifestService.calculate_file_hash(manifest_path)
                if game.manifest_hash != manifest_hash:
                    # Manifest changed, re-generate
                    return await self.generate_manifest_for_game(game, game_path, force=True, db=db)
                else:
                    # Manifest unchanged, load existing manifest
                    manifest_service = ManifestService(manifest_path)
                    manifest = manifest_service.load_manifest()
                    return manifest
            else:
                # Manifest file missing, generate new manifest
                return await self.generate_manifest_for_game(game, game_path, force=True, db=db)
        
    async def generate_manifest_for_game(self, game: Game, game_path: Path, force: bool, db: Session) -> Optional[Dict[str, Any]]:
        """Generate manifest for a specific game"""
        manifest_path = game_path / 'manifest.json'
        if manifest_path.exists():
            if not force:
                # Manifest already exists, skip generation
                logger.info(f"Manifest already exists for game {game.name}, skipping generation")
                return None
            else:
                logger.info(f"Force regenerating manifest for game {game.name}")
                manifest_path.unlink()
        time_start = asyncio.get_event_loop().time()
        manifest = await ManifestService.generate_manifest(game_path)
        time_end = asyncio.get_event_loop().time()
        if manifest:
            manifest_hash = await ManifestService.calculate_file_hash(manifest_path)
            update_game_manifest_hash(db, game.id, manifest_hash)
            update_game_size(db, game.id, manifest.get('total_size'))
            logger.info(f"Generated manifest for game {game.name} (ID: {game.id}) in {time_end - time_start:.2f} seconds")
        else:
            logger.error(f"Failed to generate manifest for game {game.name} (ID: {game.id}) in {time_end - time_start:.2f} seconds")
        return manifest
    
    async def ensure_game_entry(self, db: Session, game_path: Path) -> Optional[Any]:
        """
        Ensure game entry exists in database, create if not exists
        
        Args:
            db: Database session
            game_path: Path to the game directory
            
        Returns:
            Game database model instance or None if failed
        """
        try:
            # Check if game already exists
            existing_game = get_game_by_path(db, game_path)
            if existing_game:
                logger.info(f"Game already exists in database: {existing_game.name}")
                return existing_game
            
            # Create new game entry
            # Parse folder name to extract potential game title
            # Remove common patterns like version numbers, editions, etc.
            game_title = self.parse_game_title(game_path.name)
            
            game_data = GameCreate(
                title=game_title,
                path=game_path
            )
            
            new_game = create_game(db, game_data)
            logger.info(f"Created new game entry: {new_game.name} (ID: {new_game.id})")
            
            return new_game
            
        except Exception as e:
            logger.error(f"Failed to ensure game entry for {game_path}: {e}", exc_info=True)
            return None
        
    def parse_game_title(self, folder_name: str) -> str:
        """
        Parse game title from folder name
        
        Removes common patterns like:
        - Version numbers (v1.0, v2.3.4)
        - Edition markers (GOTY, Deluxe, Complete)
        - Platform markers (Windows, PC)
        - Common separators (underscores, dashes)
        - Prefix ([xxxxx])
        
        Args:
            folder_name: Original folder name
            
        Returns:
            Cleaned game title
        """
        import re
        
        # Replace underscores and multiple spaces with single space
        title = folder_name.replace('_', ' ')
        title = re.sub(r'\s+', ' ', title)
        
        # Remove common edition markers (case-insensitive)
        edition_patterns = [
            r'\s*-?\s*GOTY\s*',
            r'\s*-?\s*Deluxe\s*Edition\s*',
            r'\s*-?\s*Complete\s*Edition\s*',
            r'\s*-?\s*Game\s*of\s*the\s*Year\s*',
            r'\s*-?\s*Definitive\s*Edition\s*',
            r'\s*-?\s*Enhanced\s*Edition\s*',
            r'\s*-?\s*Remastered\s*',
            r'\s*-?\s*HD\s*',
            r'\s*-?\s*\[.*?\]\s*',
        ]
        
        for pattern in edition_patterns:
            title = re.sub(pattern, ' ', title, flags=re.IGNORECASE)
        
        # Remove version numbers (v1.0, v2.3.4, etc.)
        title = re.sub(r'\s*v?\d+\.\d+(\.\d+)?\s*', ' ', title, flags=re.IGNORECASE)
        
        # Remove platform markers
        title = re.sub(r'\s*-?\s*(Windows|PC|Mac|Linux)\s*', ' ', title, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title if title else folder_name
    
    async def process_metadata_scrape(self, db: Session, game: Game, force=False) -> None:
        """
        Internal task to scrape metadata for a game
        
        Args:
            db: Database session
            game: Game database model instance
        """
        if game.scraped_at:
            if not force:
                logger.info(f"Metadata of game {game.name} already scraped at {game.scraped_at}, skipping")
                return
            else:
                logger.info(f"Force re-scraping metadata for game {game.name}")
        try:
            logger.info(f"Scraping metadata for: {game.name}")
            
            # Queue the game for metadata scraping with normal priority
            success = await metadataScraperService.scrape_game_metadata(
                game=game,
                db=db,
                priority=False
            )
            
            if success:
                logger.info(f"Metadata scraping queued successfully for: {game.name}")
            else:
                logger.warning(f"Failed to queue metadata scraping for: {game.name}")
                
        except Exception as e:
            logger.error(f"Failed to scrape metadata for {game.name}: {e}", exc_info=True)