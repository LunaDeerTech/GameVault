"""Directory scanning service for game discovery"""
import os
from pathlib import Path
from typing import List, Dict


class GameScanner:
    """Service for scanning directories and discovering games"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    async def scan_directory(self) -> List[Dict]:
        """
        Scan the configured directory for game folders
        Returns list of discovered game folders with basic info
        """
        # TODO: Implement directory scanning
        pass
    
    async def generate_manifest(self, game_path: Path) -> Dict:
        """
        Generate manifest.json for a game directory
        Contains file fingerprints (path, size, modified time, hash)
        """
        # TODO: Implement manifest generation
        pass
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash for a file
        """
        # TODO: Implement file hashing
        pass
