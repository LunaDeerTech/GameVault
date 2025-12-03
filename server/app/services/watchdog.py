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
from app.core.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class FileChangeBatch:
    """Class to batch file change events"""
    
    def __init__(self):
        self.added_files: Set[Path] = set()
        self.modified_files: Set[Path] = set()
        self.removed_files: Set[Path] = set()

class DirectoryEventHandler(FileSystemEventHandler):
    """Event handler for file system events in directories with debouncing"""
    
    def __init__(self, watchdog_service: 'WatchdogService', debounce_seconds: float = 30.0):
        """
        Initialize event handler with reference to watchdog service
        
        Args:
            watchdog_service: The watchdog service to handle batched changes
            debounce_seconds: Time to wait after last change before triggering handler (default: 2.0 seconds)
        """
        self.watchdog_service = watchdog_service
        self.debounce_seconds = debounce_seconds
        self.batch = FileChangeBatch()
        self.debounce_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self.folder_only = False
    
    def _schedule_debounce(self) -> None:
        """Schedule or reschedule the debounce timer"""
        # Cancel existing debounce task if it exists
        if self.debounce_task and not self.debounce_task.done():
            self.debounce_task.cancel()
        
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, use the watchdog service's loop if available
            loop = self.watchdog_service.loop
            if loop is None:
                logger.warning("No event loop available for debouncing")
                return
        
        # Schedule new debounce task
        self.debounce_task = loop.create_task(self._debounce_timer())
    
    async def _debounce_timer(self) -> None:
        """Wait for debounce period and then trigger handler"""
        try:
            await asyncio.sleep(self.debounce_seconds)
            
            # After waiting, process the batched changes
            async with self._lock:
                if self.batch.added_files or self.batch.modified_files or self.batch.removed_files:
                    logger.info(
                        f"Debounce triggered: {len(self.batch.added_files)} added, "
                        f"{len(self.batch.modified_files)} modified, "
                        f"{len(self.batch.removed_files)} removed"
                    )
                    await self.watchdog_service.handle_file_change(self.batch)
                    # Reset batch after processing
                    self.batch = FileChangeBatch()
        except asyncio.CancelledError:
            # Task was cancelled, which is normal when new events arrive
            pass
        except Exception as e:
            logger.error(f"Error in debounce timer: {e}", exc_info=True)
    
    def _add_to_batch(self, file_path: Path, change_type: str) -> None:
        """
        Add file change to batch and schedule debounce
        
        Args:
            file_path: Path of the changed file
            change_type: Type of change ('added', 'modified', 'removed')
        """

        if change_type == 'added' and file_path not in self.batch.added_files:
            if self.folder_only and not file_path.is_dir():
                return
            self.batch.added_files.add(file_path)
            # Remove from removed set if it was previously marked as removed
            self.batch.removed_files.discard(file_path)
        elif change_type == 'modified' and file_path not in self.batch.modified_files:
            if self.folder_only and not file_path.is_dir():
                return
            self.batch.modified_files.add(file_path)
        elif change_type == 'removed' and file_path not in self.batch.removed_files:
            self.batch.removed_files.add(file_path)
            # Remove from added and modified sets
            self.batch.added_files.discard(file_path)
            self.batch.modified_files.discard(file_path)
        
        # Schedule/reschedule debounce timer
        self._schedule_debounce()
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file/directory modification events"""
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        logger.debug(f"File modified: {file_path}")
        self._add_to_batch(file_path, 'modified')
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file/directory creation events"""
        file_path = Path(event.src_path)
        logger.debug(f"File created: {file_path}")
        self._add_to_batch(file_path, 'added')
        
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file/directory deletion events"""
        file_path = Path(event.src_path)
        logger.debug(f"File deleted: {file_path}")
        self._add_to_batch(file_path, 'removed')
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file/directory move/rename events"""
        src_path = Path(event.src_path)
        dest_path = Path(event.dest_path)
        logger.debug(f"File moved: {src_path} -> {dest_path}")
        # Treat move as deletion of old path and creation of new path
        self._add_to_batch(src_path, 'removed')
        self._add_to_batch(dest_path, 'added')
    
    
class WatchdogService:
    """Abstract watchdog service class"""
    
    def __init__(self, path: Path, event_handler: DirectoryEventHandler):
        self.path = path
        self.observer = Observer()
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.event_handler = event_handler
        
    async def start(self, folder_only: bool = False):
        """Start the watchdog service"""
        # Store reference to the current event loop
        self.loop = asyncio.get_running_loop()
        self.event_handler.folder_only = folder_only
        self.observer.schedule(
            self.event_handler,
            str(self.path),
            recursive=True
        )
        self.observer.start()
    
    async def stop(self):
        """Stop the watchdog service"""
        self.observer.stop()
        self.observer.join()
    
    async def handle_file_change(self, file_changes: FileChangeBatch):
        """Handle file change events"""
        logger.debug("WatchdogService class Not implemented: handle_file_change")
        raise NotImplementedError("handle_file_change method must be implemented by subclasses")