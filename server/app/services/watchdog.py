"""Watchdog service for monitoring game directories changes"""
import asyncio
from enum import Enum
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime, timezone

from app.models.game import Game
from app.schemas.manifest import GameManifest
from app.services.scanner import initial_scanner_service
from app.core.config import settings

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
        # Queue the file change for processing
        asyncio.create_task(
            self.watchdog_service.handle_file_change(file_path, EventType.MODIFIED)
        )
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file/directory creation events"""
        file_path = Path(event.src_path)
        asyncio.create_task(
            self.watchdog_service.handle_file_change(file_path, EventType.CREATED)
        )
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file/directory deletion events"""
        file_path = Path(event.src_path)   
        # Queue the file change for processing
        asyncio.create_task(
            self.watchdog_service.handle_file_change(file_path, EventType.DELETED)
        )
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file/directory move/rename events"""
        src_path = Path(event.src_path)
        dest_path = Path(event.dest_path)
        # Handle file move as deletion + creation
        asyncio.create_task(
            self.watchdog_service.handle_file_change(src_path, EventType.DELETED)
        )
        asyncio.create_task(
            self.watchdog_service.handle_file_change(dest_path, EventType.CREATED)
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
    
    async def start_monitoring(self) -> None:
        """Start monitoring game directories for changes"""
        if self.is_monitoring:
            return  # Already monitoring
        # List all game directories and add to tracking set
        if self.games_directory.exists() and self.games_directory.is_dir():
            for item in self.games_directory.iterdir():
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if not manifest_path.exists():
                        # Skip monitoring directories without manifest
                        # Use initial scanner to generate manifest first asynchronously
                        # After manifest is created, watchdog will pick up changes
                        logger.info(f"Game directory {item} missing manifest.json, triggering scan")
                        initial_scanner_service.scan_game_directory(item)
                        continue
                    else:
                        logger.info(f"Monitoring game directory: {item}")
                        self.game_directories[item] = {
                            "last_updated": datetime.now(settings.TZ),
                            "need_update": False,
                            "status": GameDirectoryStatus.IDLE,
                            "update_list": {
                                "added": [],
                                "updated": [],
                                "removed": []
                            }
                        }
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
        self.game_directories.clear()
        self.observer.stop()
        self.observer.join()
        self.is_monitoring = False
        logger.info("Stopped monitoring game directories")
    
    async def handle_file_change(self, file_path: Path, event_type: EventType) -> None:
        """
        Handle individual file change events
        
        Args:
            file_path: Path to the changed file
            event_type: Type of change (created, modified, deleted, moved)
        """
        # TODO: Implement file change handling
        pass
    
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
    

