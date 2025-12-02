"""Watchdog service for monitoring game directories changes"""
import asyncio
from enum import Enum
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime, timezone

from app.models.game import Game
from app.schemas.manifest import GameManifest
from app.services.scanner import initialScannerService
from app.core.config import settings
from app.crud.game import get_game, update_game
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of file system events"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"

class GameDirectoryEventHandler(FileSystemEventHandler):
    """Event handler for file system events in game directories"""
    
    def __init__(self, watchdog_service: 'GameWatchdogService'):
        """Initialize event handler with reference to watchdog service"""
        self.watchdog_service = watchdog_service
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file/directory modification events"""
        file_path = Path(event.src_path)
        # Queue the file change for processing using run_coroutine_threadsafe
        # since watchdog runs in a separate thread
        if self.watchdog_service.loop:
            asyncio.run_coroutine_threadsafe(
                self.watchdog_service.handle_file_change(file_path, EventType.MODIFIED),
                self.watchdog_service.loop
            )
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file/directory creation events"""
        file_path = Path(event.src_path)
        if self.watchdog_service.loop:
            asyncio.run_coroutine_threadsafe(
                self.watchdog_service.handle_file_change(file_path, EventType.CREATED),
                self.watchdog_service.loop
            )
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file/directory deletion events"""
        file_path = Path(event.src_path)   
        # Queue the file change for processing using run_coroutine_threadsafe
        # since watchdog runs in a separate thread
        if self.watchdog_service.loop:
            asyncio.run_coroutine_threadsafe(
                self.watchdog_service.handle_file_change(file_path, EventType.DELETED),
                self.watchdog_service.loop
            )
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file/directory move/rename events"""
        src_path = Path(event.src_path)
        dest_path = Path(event.dest_path)
        # Handle file move as deletion + creation
        if self.watchdog_service.loop:
            asyncio.run_coroutine_threadsafe(
                self.watchdog_service.handle_file_change(src_path, EventType.DELETED),
                self.watchdog_service.loop
            )
            asyncio.run_coroutine_threadsafe(
                self.watchdog_service.handle_file_change(dest_path, EventType.CREATED),
                self.watchdog_service.loop
            )

class GameDirectoryStatus(Enum):
    """Status of game directory monitoring"""
    IDLE = "idle"
    UPDATING = "updating"

class GameWatchdogService:
    """Service for monitoring game directory changes and triggering updates"""
    
    def __init__(self, games_directory: Path):
        """
        Initialize watchdog service
        
        Args:
            games_directory: Path to the games directory to monitor
                e.g. /path/to/games
                        - Game1
                        - Game2
            scanner_service: Scanner service for generating manifests
        """
        self.games_directory = games_directory
        self.observer = Observer()
        self.event_handler = GameDirectoryEventHandler(self)
        self.is_monitoring = False
        self.game_directories: Dict[Path, Dict] = {}  # Set of game directories
        self.update_delay = 60  # Delay in seconds before triggering update
        self.pending_update_tasks: Dict[Path, asyncio.Task] = {}  # Track pending update tasks
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # Store reference to main event loop
    
    async def start_monitoring(self) -> None:
        """Start monitoring game directories for changes"""
        if self.is_monitoring:
            return  # Already monitoring
        
        # Store reference to the current event loop for use by watchdog thread
        self.loop = asyncio.get_running_loop()
        
        # List all game directories and add to tracking set
        if self.games_directory.exists() and self.games_directory.is_dir():
            for item in self.games_directory.iterdir():
                if item.is_dir():
                    asyncio.create_task(self.new_game_added(item))
        else:
            raise ValueError(f"Games directory {self.games_directory} does not exist or is not a directory")
        
        self.observer.schedule(
            self.event_handler,
            str(self.games_directory),
            recursive=True
        )
        self.observer.start()
        self.is_monitoring = True
        logger.info("Started monitoring game directories")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring game directories"""
        if not self.is_monitoring:
            return  # Not currently monitoring
        
        # Cancel all pending update tasks
        for task in self.pending_update_tasks.values():
            if not task.done():
                task.cancel()
        self.pending_update_tasks.clear()
        
        self.game_directories.clear()
        self.observer.stop()
        self.observer.join()
        self.is_monitoring = False
        self.loop = None  # Clear the event loop reference
        logger.info("Stopped monitoring game directories")
    
    async def handle_file_change(self, file_path: Path, event_type: EventType) -> None:
        """
        Handle individual file change events
        
        Args:
            file_path: Path to the changed file
            event_type: Type of change (created, modified, deleted, moved)
        """
        if not self.is_monitoring:
            return  # Ignore events if not monitoring
        if self.should_ignore_file(file_path):
            return  # Ignore temporary or irrelevant files
        
        game_dir = file_path.relative_to(self.games_directory).parts[0]
        game_dir_path = self.games_directory / game_dir
        
        if file_path.name == "manifest.json":
            if event_type == EventType.CREATED:
                # manifest created means the game is added, we can start monitoring it
                asyncio.create_task(self.new_game_added(game_dir_path))
                return
            if event_type == EventType.MODIFIED:
                # manifest modified should not be take into account about game update
                # because it represents the result of an update, we can just ignore it
                return
            if event_type == EventType.DELETED:
                # manifest deleted means the game is removed, we can stop monitoring it
                if game_dir_path in self.game_directories:
                    del self.game_directories[game_dir_path]
                    logger.info(f"Stopped monitoring game directory (manifest deleted): {game_dir_path} will be re-added on next scan")
        
        if game_dir_path not in self.game_directories:
            # it is a new game add
            asyncio.create_task(self.new_game_added(game_dir_path))
            return
        
        game_file_change_info = self.game_directories[game_dir_path]
        if event_type == EventType.CREATED:
            game_file_change_info["update_list"]["added"].append(file_path)
        elif event_type == EventType.MODIFIED:
            game_file_change_info["update_list"]["updated"].append(file_path)
        elif event_type == EventType.DELETED:
            game_file_change_info["update_list"]["removed"].append(file_path)
        game_file_change_info["need_update"] = True        
        game_file_change_info["last_updated"] = datetime.now(settings.TZ)
        
        # Schedule delayed update with debounce mechanism
        await self._schedule_delayed_update(game_dir_path, game_file_change_info)
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored from monitoring
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be ignored (temp files, logs, etc.)
        """
        # TODO: Implement file ignore logic
        pass
    
    async def get_monitoring_status(self) -> Dict[str, any]:
        """
        Get current monitoring status and statistics
        
        Returns:
            Dictionary containing monitoring status information
        """
        return {
            "is_monitoring": self.is_monitoring,
            # Add more stats as needed
        }
        
    async def _schedule_delayed_update(self, game_dir_path: Path, game_file_change_info: Dict) -> None:
        """
        Schedule a delayed update with debounce mechanism.
        If there's already a pending update task, cancel it and reschedule.
        
        Args:
            game_dir_path: Path to the game directory
            game_file_change_info: Dictionary containing game update information
        """
        # Cancel existing pending update task if any
        if game_dir_path in self.pending_update_tasks:
            existing_task = self.pending_update_tasks[game_dir_path]
            if not existing_task.done():
                existing_task.cancel()
                try:
                    await existing_task
                except asyncio.CancelledError:
                    pass  # Expected when canceling
        
        # Create new delayed update task
        async def delayed_update():
            try:
                logger.debug(f"Waiting {self.update_delay}s before updating {game_dir_path.name}")
                await asyncio.sleep(self.update_delay)
                
                # After delay, trigger the actual update
                logger.info(f"Triggering update for {game_dir_path.name}")
                await self.trigger_updates(game_dir_path, game_file_change_info)
                
                # Clean up the task from pending tasks
                if game_dir_path in self.pending_update_tasks:
                    del self.pending_update_tasks[game_dir_path]
            except asyncio.CancelledError:
                logger.debug(f"Update task for {game_dir_path.name} was cancelled (new changes detected)")
                raise
        
        # Schedule the new task
        self.pending_update_tasks[game_dir_path] = asyncio.create_task(delayed_update())
    
    
    async def trigger_updates(self, path: Path, game_update_info: Dict) -> None:
        pass
    
    async def new_game_added(self, path: Path) -> None:
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            # Skip monitoring directories without manifest
            # Use initial scanner to generate manifest first asynchronously
            # After manifest is created, watchdog will pick up changes
            logger.info(f"Game directory {path} missing manifest.json, triggering scan")
            initialScannerService.scan_game_directory(path)
            return
        else:
            logger.info(f"Monitoring game directory: {path}")
            # read existing manifest to initialize state
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            game = get_game(SessionLocal(), manifest_data["game_id"])
            
            if not game:
                # Game not found in database, log warning
                logger.warning(f"Game with ID {manifest_data['game_id']} not found in database, deleting manifest to trigger re-scan")
                manifest_path.unlink(missing_ok=True) # Delete manifest to trigger re-scan
                return
            
            if game.path != str(path):
                logger.warning(f"Game path mismatch for game ID {game.id}, updating path from {game.path} to {path}")
                game.path = str(path)
                # Update the game record in the database or wherever it is stored
                update_game(SessionLocal(), game.id, game)
                
            self.game_directories[path] = {
                "last_updated": datetime.now(settings.TZ),
                "need_update": False,
                "status": GameDirectoryStatus.IDLE,
                "update_list": {
                    "added": [],
                    "updated": [],
                    "removed": []
                }
            }
    

    

