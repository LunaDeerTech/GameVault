"""Directory scanning service for game discovery"""
import os
from pathlib import Path
from typing import List, Dict


class GameScanner:
    """Service for scanning directories and discovering games"""
    
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
        self.pending_scans: Dict[Path, bool] = {} # path -> is_scanning
    
    async def scan_directory(self) -> List[Dict]:
        """
        Scan the configured directory for game folders
        Returns list of discovered game folders with basic info
        """
        # TODO: Implement directory scanning
        pass
    
    async def generate_game_info(self, game_path: Path) -> Dict:
        """
        Generate basic game info from a game folder:
            1. Create database entry if not exists
            2. Generate detailed info parallely:
                a. Generate manifest.json for the game folder
                    then update database with manifest info
                c. Add to Scraper queue for metadata fetching
    
        Args:
            game_path: Path to the individual game folder
        """
        # TODO: Implement manifest generation
        pass
    
