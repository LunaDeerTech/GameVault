"""Watchdog service for monitoring game directories changes"""
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime

from app.models.game import Game
from app.schemas.manifest import GameManifest
from app.services.scanner import GameScanner


class GameDirectoryEventHandler(FileSystemEventHandler):
    """Event handler for file system events in game directories"""
    
    def __init__(self, watchdog_service: 'GameWatchdogService'):
        """Initialize event handler with reference to watchdog service"""
        self.watchdog_service = watchdog_service
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file/directory modification events"""
        if event.is_directory:
            return  # Skip directory modification events
        
        file_path = Path(event.src_path)
        
        # Check if file should be ignored
        if self.watchdog_service.should_ignore_file(file_path):
            return
        
        # Queue the file change for processing
        asyncio.create_task(
            self.watchdog_service.handle_file_change(file_path, "modified")
        )
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file/directory creation events"""
        file_path = Path(event.src_path)
        
        if event.is_directory:
            # Check if new directory is a game directory
            if self.watchdog_service.is_game_directory(file_path):
                # Start monitoring the new game directory
                self.watchdog_service.observer.schedule(
                    self.watchdog_service.event_handler,
                    str(file_path),
                    recursive=True
                )
                # Queue for full manifest generation
                asyncio.create_task(
                    self.watchdog_service.queue_manifest_update(file_path)
                )
            return
        
        # Check if file should be ignored
        if self.watchdog_service.should_ignore_file(file_path):
            return
        
        # Queue the file change for processing
        asyncio.create_task(
            self.watchdog_service.handle_file_change(file_path, "created")
        )
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file/directory deletion events"""
        file_path = Path(event.src_path)
        
        if event.is_directory:
            # If a game directory was deleted, remove from monitoring
            game_path = self.watchdog_service.get_game_from_path(file_path)
            if game_path and game_path == file_path:
                # Notify about game directory deletion
                for callback in self.watchdog_service.update_callbacks:
                    try:
                        callback(file_path, "game_deleted")
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Error in update callback: {e}")
            return
        
        # Check if file should be ignored
        if self.watchdog_service.should_ignore_file(file_path):
            return
        
        # Queue the file change for processing
        asyncio.create_task(
            self.watchdog_service.handle_file_change(file_path, "deleted")
        )
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file/directory move/rename events"""
        src_path = Path(event.src_path)
        dest_path = Path(event.dest_path)
        
        if event.is_directory:
            # Handle game directory rename/move
            src_game_path = self.watchdog_service.get_game_from_path(src_path)
            dest_game_path = self.watchdog_service.get_game_from_path(dest_path)
            
            if src_game_path and src_game_path == src_path:
                # Game directory was moved/renamed
                if dest_game_path and dest_game_path == dest_path:
                    # Still a valid game directory, update monitoring
                    asyncio.create_task(
                        self.watchdog_service.handle_file_change(dest_path, "game_moved")
                    )
                else:
                    # No longer a valid game directory
                    for callback in self.watchdog_service.update_callbacks:
                        try:
                            callback(src_path, "game_deleted")
                        except Exception as e:
                            print(f"Error in update callback: {e}")
            return
        
        # Check if files should be ignored
        if (self.watchdog_service.should_ignore_file(src_path) or 
            self.watchdog_service.should_ignore_file(dest_path)):
            return
        
        # Handle file move as deletion + creation
        asyncio.create_task(
            self.watchdog_service.handle_file_change(src_path, "deleted")
        )
        asyncio.create_task(
            self.watchdog_service.handle_file_change(dest_path, "created")
        )


class GameWatchdogService:
    """Service for monitoring game directory changes and triggering updates"""
    
    def __init__(self, games_directory: Path, scanner_service: GameScanner):
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
        self.scanner_service = scanner_service
        self.observer = Observer()
        self.event_handler = GameDirectoryEventHandler(self)
        self.is_monitoring = False
        self.pending_updates: Set[Path] = set()
        self.update_callbacks: List[Callable] = []
    
    async def start_monitoring(self) -> None:
        """Start monitoring game directories for changes"""
        # TODO: Implement monitoring startup
        pass
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring game directories"""
        # TODO: Implement monitoring shutdown
        pass
    
    def add_update_callback(self, callback: Callable[[Path, str], None]) -> None:
        """
        Add callback function to be called when updates are detected
        
        Args:
            callback: Function to call with (game_path, event_type) when changes occur
        """
        # TODO: Implement callback registration
        pass
    
    def remove_update_callback(self, callback: Callable[[Path, str], None]) -> None:
        """
        Remove update callback function
        
        Args:
            callback: Function to remove from callbacks list
        """
        # TODO: Implement callback removal
        pass
    
    async def handle_file_change(self, file_path: Path, event_type: str) -> None:
        """
        Handle individual file change events
        
        Args:
            file_path: Path to the changed file
            event_type: Type of change (created, modified, deleted, moved)
        """
        # TODO: Implement file change handling
        pass
    
    async def queue_manifest_update(self, game_path: Path) -> None:
        """
        Queue a game directory for manifest update
        
        Args:
            game_path: Path to the game directory that needs manifest update
        """
        # TODO: Implement manifest update queuing
        pass
    
    async def process_pending_updates(self) -> None:
        """Process all pending manifest updates in batch"""
        # TODO: Implement batch update processing
        pass
    
    async def regenerate_manifest(self, game_path: Path) -> Optional[GameManifest]:
        """
        Regenerate manifest for a specific game directory
        
        Args:
            game_path: Path to the game directory
            
        Returns:
            Updated GameManifest or None if failed
        """
        # TODO: Implement manifest regeneration
        pass
    
    async def validate_manifest_integrity(self, game_path: Path) -> bool:
        """
        Validate that current files match the stored manifest
        
        Args:
            game_path: Path to the game directory
            
        Returns:
            True if manifest matches current files
        """
        # TODO: Implement manifest integrity validation
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
        # TODO: Implement status reporting
        pass
    
    def add_game_directory(self, directory_path: str) -> None:
        """
        Add a new game directory to monitor
        
        Args:
            directory_path: Path to the game directory to add
        """
        # TODO: Implement dynamic directory addition
        pass
    
    def remove_game_directory(self, directory_path: str) -> None:
        """
        Remove a game directory from monitoring
        
        Args:
            directory_path: Path to the game directory to remove
        """
        # TODO: Implement dynamic directory removal
        pass

