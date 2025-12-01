"""Metadata scraping service from Steam/IGDB"""
import random
import string
import httpx
import asyncio
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path
from app.models.game import Game
from app.schemas.game import GameUpdate
from app.crud.game import update_game
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MetadataScraper:
    """Service for scraping game metadata from external APIs"""
    
    def __init__(self, igdb_client_id: str = "", igdb_client_secret: str = "", max_workers: int = 5):
        self.max_workers = max_workers  # Max concurrent scraping tasks
        
        # Task queue with priority support: (priority_level, game_id, game, db)
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._active_tasks: set = set()
        self._workers: list = []
        self._running = False
        
        self.steam_scraper = SteamScraper()
        self.igdb_scraper = IGDBScraper(igdb_client_id, igdb_client_secret)
    
    async def start(self):
        """Start the scraper worker pool"""
        if self._running:
            logger.warning("Scraper is already running")
            return
        
        self._running = True
        logger.info(f"Starting MetadataScraper with {self.max_workers} workers")
        
        # Create worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
    
    async def stop(self):
        """Stop the scraper worker pool gracefully"""
        if not self._running:
            return
        
        logger.info("Stopping MetadataScraper...")
        self._running = False
        
        # Wait for all workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("MetadataScraper stopped")
    
    async def _worker(self, worker_id: int):
        """Worker coroutine that processes tasks from the queue"""
        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Wait for a task with timeout to allow checking _running flag
                try:
                    priority, game_id, game, db = await asyncio.wait_for(
                        self._task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                logger.info(f"Worker {worker_id} processing game_id={game_id}, priority={priority}")
                self._active_tasks.add(game_id)
                
                try:
                    # Perform the actual scraping
                    await self._scrape_game_metadata_internal(game, db)
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to scrape game_id={game_id}: {e}", exc_info=True)
                finally:
                    self._active_tasks.discard(game_id)
                    self._task_queue.task_done()
                    
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered error: {e}", exc_info=True)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def scrape_game_metadata(self, game: Game, db: Session, priority: bool = False) -> bool:
        """
        Scrape metadata for a game from Steam and IGDB
        
        If priority is True, prioritize this task in the queue
        If Steam AppID or IGDB ID is empty, perform search first to find them
        Then download detailed metadata from both sources
        Finally update the game database entry with new metadata
        
        Args:
            game: Game database model instance
            db: Database session
            priority: Whether to prioritize this scraping task
            
        Returns:
            success: True if task was queued successfully, False otherwise
        """
        if not self._running:
            logger.warning("Scraper is not running. Call start() first.")
            return False
        
        # Check if already in queue or being processed
        if game.id in self._active_tasks:
            logger.info(f"Game {game.id} is already being processed")
            return False
        
        # Priority: 0 = highest, 1 = normal
        priority_level = 0 if priority else 1
        
        try:
            await self._task_queue.put((priority_level, game.id, game, db))
            logger.info(f"Queued game_id={game.id} with priority={priority_level}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue game_id={game.id}: {e}")
            return False
    
    async def _scrape_game_metadata_internal(self, game: Game, db: Session) -> bool:
        """
        Internal method to scrape and update game metadata
        
        Args:
            game: Game database model instance
            db: Database session
            
        Returns:
            success: True if metadata scraping and updating succeeded, False otherwise
        """
        try:
            logger.info(f"Starting metadata scraping for game: {game.name} (ID: {game.id})")
            
            # Step 1: Search for Steam AppID if not present
            steam_app_id = None
            if game.steam_id:
                try:
                    steam_app_id = int(game.steam_id)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid steam_id for game {game.id}: {game.steam_id}")
            
            if not steam_app_id:
                logger.info(f"Searching Steam for game: {game.name}")
                steam_app_id = await self.steam_scraper.search_steam(game.name)
                if steam_app_id:
                    logger.info(f"Found Steam AppID: {steam_app_id}")
            
            # Step 2: Search for IGDB ID if not present
            igdb_id = None
            if game.igdb_id:
                try:
                    igdb_id = int(game.igdb_id)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid igdb_id for game {game.id}: {game.igdb_id}")
            
            if not igdb_id:
                logger.info(f"Searching IGDB for game: {game.name}")
                igdb_id = await self.igdb_scraper.search_igdb(game.name)
                if igdb_id:
                    logger.info(f"Found IGDB ID: {igdb_id}")
            
            # Step 3: Download metadata from both sources in parallel
            steam_metadata = None
            igdb_metadata = None
            
            tasks = []
            if steam_app_id:
                tasks.append(self.steam_scraper.download_steam_metadata(steam_app_id))
            if igdb_id:
                tasks.append(self.igdb_scraper.download_igdb_metadata(igdb_id))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                result_idx = 0
                if steam_app_id:
                    steam_result = results[result_idx]
                    result_idx += 1
                    if isinstance(steam_result, Exception):
                        logger.error(f"Failed to download Steam metadata: {steam_result}")
                    else:
                        steam_metadata = steam_result
                
                if igdb_id:
                    igdb_result = results[result_idx]
                    if isinstance(igdb_result, Exception):
                        logger.error(f"Failed to download IGDB metadata: {igdb_result}")
                    else:
                        igdb_metadata = igdb_result
            
            # Step 4: Merge metadata (IGDB takes precedence for conflicts)
            merged_metadata = self._merge_metadata(steam_metadata, igdb_metadata)
            
            # Add discovered IDs
            if steam_app_id and not merged_metadata.steam_id:
                merged_metadata.steam_id = steam_app_id
            if igdb_id and not merged_metadata.igdb_id:
                merged_metadata.igdb_id = igdb_id
            
            # Step 5: Update game in database
            if merged_metadata:
                updated_game = update_game(db, game.id, merged_metadata)
                if updated_game:
                    logger.info(f"Successfully updated game metadata for: {game.name}")
                    return True
                else:
                    logger.error(f"Failed to update game in database: {game.name}")
                    return False
            else:
                logger.warning(f"No metadata available to update for: {game.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error scraping metadata for game {game.id}: {e}", exc_info=True)
            return False
    
    def _merge_metadata(self, steam_data: Optional[GameUpdate], igdb_data: Optional[GameUpdate]) -> Optional[GameUpdate]:
        """
        Merge metadata from Steam and IGDB sources
        IGDB takes precedence for conflicts
        
        Args:
            steam_data: Metadata from Steam
            igdb_data: Metadata from IGDB
            
        Returns:
            Merged GameUpdate object
        """
        if not steam_data and not igdb_data:
            return None
        
        if not steam_data:
            return igdb_data
        
        if not igdb_data:
            return steam_data
        
        # Create merged result, IGDB takes precedence
        merged = GameUpdate()
        
        # Iterate through all fields and merge
        for field in steam_data.model_fields.keys():
            steam_value = getattr(steam_data, field, None)
            igdb_value = getattr(igdb_data, field, None)
            
            # IGDB takes precedence if value exists
            if igdb_value is not None:
                setattr(merged, field, igdb_value)
            elif steam_value is not None:
                setattr(merged, field, steam_value)
        
        return merged
    
    def get_queue_size(self) -> int:
        """Get the current size of the task queue"""
        return self._task_queue.qsize()
    
    def get_active_tasks(self) -> int:
        """Get the number of currently active tasks"""
        return len(self._active_tasks)
    
    def is_running(self) -> bool:
        """Check if the scraper is running"""
        return self._running


async def download_image(url: str, save_path: Path) -> None:
    """
    Download image from URL and save to specified path
    Args:
        url: Image URL
        save_path: Local path to save the image
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Get suffix from URL
            suffix = Path(url).suffix
            
            # Ensure directory exists
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Generate random filename with alphanumeric characters
            random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            final_path = save_path / (random_filename + suffix)
            
            # Write image to file
            with open(final_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image to: {final_path}")
            
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")


class SteamScraper():
    async def search_steam(self, game_name: str) -> int:
        """
        Search for game on Steam by name
        Returns steam AppID
        """
        # TODO: Implement Steam API search
        pass
    
    async def download_steam_metadata(self, app_id: int) -> GameUpdate:
        """
        Download detailed metadata for a game from Steam by AppID
        Returns new game metadata to update
        """
        pass

class IGDBScraper():
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def search_igdb(self, game_name: str) -> int:
        """
        Search for game on IGDB by name
        Returns IGDB ID
        """
        # TODO: Implement IGDB API search
        pass
    
    async def download_igdb_metadata(self, igdb_id: int) -> GameUpdate:
        """
        Download detailed metadata for a game from IGDB by IGDB ID
        Returns new game metadata to update
        """
        pass