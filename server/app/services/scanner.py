"""Game directory scan service"""
import asyncio
import logging
from pathlib import Path
from app.services.manifest import ManifestService
from app.services.scraper import metadataScraperService


logger = logging.getLogger(__name__)

class InitialScannerService:
    """Service to perform initial scan of game directories"""
    
    def __init__(self):
        """Initialize with a callback to process each game directory"""
        pass
    
    def start(self, max_concurrent_scans: int = 3) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent_scans)
        
    def scan_game_directory(self, game_path: Path) -> None:
        """Add a game directory to the scan queue"""
        pass
        
        
    async def _scan_game_directory_task(self, game_path: Path) -> None:
        """Internal task to scan a game directory"""
        # 1. create game database entry if not exists
        # 2. generate manifest.json
        # 3. scrape metadata from Steam/IGDB
    
    async def _manifest_scan_task(self, game_path: Path) -> None:
        """Internal task to scan a single game directory"""
        pass
    
    async def _metadata_scrape_task(self, game_path: Path) -> None:
        """Internal task to scrape metadata for a single game"""
        pass
    
initial_scanner_service = InitialScannerService()