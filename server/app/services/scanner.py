"""Game directory scan service"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.manifest import ManifestService
from app.services.scraper import metadataScraperService
from app.crud.game import (
    get_game_by_folder_name, 
    create_game, 
    update_game_manifest_hash,
    update_game_size
)
from app.schemas.game import GameCreate
from app.core.database import SessionLocal


logger = logging.getLogger(__name__)


class InitialScannerService:
    """Service to perform initial scan of game directories"""
    
    def __init__(self):
        """Initialize scanner service"""
        self._running = False
        self._scan_tasks = []
        self.semaphore = None
        
    def start(self, max_concurrent_scans: int = 3) -> None:
        """
        Start the scanner service with controlled concurrency
        
        Args:
            max_concurrent_scans: Maximum number of concurrent scanning operations
        """
        self.semaphore = asyncio.Semaphore(max_concurrent_scans)
        self._running = True
        logger.info(f"InitialScannerService started with max_concurrent_scans={max_concurrent_scans}")
    
    async def stop(self) -> None:
        """Stop the scanner service gracefully"""
        if not self._running:
            return
        
        logger.info("Stopping InitialScannerService...")
        self._running = False
        
        # Wait for all active scan tasks to complete
        if self._scan_tasks:
            await asyncio.gather(*self._scan_tasks, return_exceptions=True)
            self._scan_tasks.clear()
        
        logger.info("InitialScannerService stopped")
    
    def scan_game_directory(self, game_path: Path) -> None:
        """
        Add a game directory to the scan queue
        
        Args:
            game_path: Path to the game directory to scan
        """
        if not self._running:
            logger.warning("Scanner is not running. Call start() first.")
            return
        
        if not game_path.exists() or not game_path.is_dir():
            logger.error(f"Invalid game directory: {game_path}")
            return
        
        # Create and track the scanning task
        task = asyncio.create_task(self._scan_game_directory_task(game_path))
        self._scan_tasks.append(task)
        
        # Cleanup completed tasks
        self._scan_tasks = [t for t in self._scan_tasks if not t.done()]
        
        logger.info(f"Queued game directory for scanning: {game_path}")
    
    async def _scan_game_directory_task(self, game_path: Path) -> None:
        """
        Internal task to scan a game directory
        
        Performs three main operations:
        1. Create game database entry if not exists
        2. Generate manifest.json for file tracking
        3. Scrape metadata from Steam/IGDB
        
        Args:
            game_path: Path to the game directory
        """
        async with self.semaphore:
            try:
                logger.info(f"Starting scan for: {game_path}")
                
                # Get database session
                db = SessionLocal()
                
                try:
                    # Step 1: Create or retrieve game database entry
                    game = await self._ensure_game_entry(db, game_path)
                    if not game:
                        logger.error(f"Failed to create/retrieve game entry for: {game_path}")
                        return
                    
                    logger.info(f"Game entry ready: {game.name} (ID: {game.id})")
                    
                    # Step 2: Generate manifest in parallel with metadata scraping
                    manifest_task = asyncio.create_task(
                        self._manifest_scan_task(db, game_path, game.id)
                    )
                    
                    # Step 3: Scrape metadata (runs in parallel with manifest generation)
                    metadata_task = asyncio.create_task(
                        self._metadata_scrape_task(db, game)
                    )
                    
                    # Wait for both tasks to complete
                    await asyncio.gather(manifest_task, metadata_task, return_exceptions=True)
                    
                    logger.info(f"Successfully completed scan for: {game.name}")
                    
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Error scanning game directory {game_path}: {e}", exc_info=True)
    
    async def _ensure_game_entry(self, db: Session, game_path: Path) -> Optional[Any]:
        """
        Ensure game entry exists in database, create if not exists
        
        Args:
            db: Database session
            game_path: Path to the game directory
            
        Returns:
            Game database model instance or None if failed
        """
        try:
            # Extract folder name as slug
            folder_name = game_path.name
            
            # Check if game already exists
            existing_game = get_game_by_folder_name(db, folder_name)
            if existing_game:
                logger.info(f"Game already exists in database: {existing_game.name}")
                return existing_game
            
            # Create new game entry
            # Parse folder name to extract potential game title
            # Remove common patterns like version numbers, editions, etc.
            game_title = self._parse_game_title(folder_name)
            
            game_data = GameCreate(
                title=game_title,
                slug=folder_name,
                description=None,
                size_bytes=0  # Will be updated after manifest generation
            )
            
            new_game = create_game(db, game_data)
            logger.info(f"Created new game entry: {new_game.name} (ID: {new_game.id})")
            
            return new_game
            
        except Exception as e:
            logger.error(f"Failed to ensure game entry for {game_path}: {e}", exc_info=True)
            return None
    
    def _parse_game_title(self, folder_name: str) -> str:
        """
        Parse game title from folder name
        
        Removes common patterns like:
        - Version numbers (v1.0, v2.3.4)
        - Edition markers (GOTY, Deluxe, Complete)
        - Platform markers (Windows, PC)
        - Common separators (underscores, dashes)
        
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
    
    async def _manifest_scan_task(self, db: Session, game_path: Path, game_id: int) -> None:
        """
        Internal task to generate manifest for a game directory
        
        Args:
            db: Database session
            game_path: Path to the game directory
            game_id: Database ID of the game
        """
        try:
            logger.info(f"Generating manifest for: {game_path}")
            
            # Generate manifest using ManifestService
            manifest = await ManifestService.generate_manifest(game_id, game_path)
            
            # Calculate manifest hash
            manifest_hash = await ManifestService.get_manifest_hash(game_path)
            
            # Update game with manifest hash and total size
            update_game_manifest_hash(db, game_id, manifest_hash)
            update_game_size(db, game_id, manifest.get('total_size', 0))
            
            logger.info(
                f"Manifest generated successfully: "
                f"{manifest.get('file_count', 0)} files, "
                f"{manifest.get('total_size', 0)} bytes"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate manifest for {game_path}: {e}", exc_info=True)
    
    async def _metadata_scrape_task(self, db: Session, game: Any) -> None:
        """
        Internal task to scrape metadata for a game
        
        Args:
            db: Database session
            game: Game database model instance
        """
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
    
    def get_active_scans(self) -> int:
        """Get the number of currently active scan tasks"""
        # Clean up completed tasks first
        self._scan_tasks = [t for t in self._scan_tasks if not t.done()]
        return len(self._scan_tasks)
    
    def is_running(self) -> bool:
        """Check if the scanner is running"""
        return self._running


# Global scanner service instance
initialScannerService = InitialScannerService()