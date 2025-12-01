"""Metadata scraping service from Steam/IGDB"""
import httpx
from typing import Optional, Dict
from app.models.game import Game
from app.schemas.game import GameUpdate


class MetadataScraper:
    """Service for scraping game metadata from external APIs"""
    
    def __init__(self, steam_api_key: str = "", igdb_client_id: str = "", igdb_client_secret: str = "", max_workers: int = 5):
        self.steam_api_key = steam_api_key
        self.igdb_client_id = igdb_client_id
        self.igdb_client_secret = igdb_client_secret
        self.max_workers = max_workers  # Max concurrent scraping tasks
        
    async def scrape_game_metadata(self, game: Game, priority: bool = False) -> bool:
        """
        Scrape metadata for a game from Steam and IGDB
        If priority is True, prioritize this task in the queue
        If Steam AppID or IGDB ID is empty, perform search first to find them
        Then download detailed metadata from both sources
        Finally update the game database entry with new metadata
        
        Args:
            game: Game database model instance
            priority: Whether to prioritize this scraping task
            
        Returns:
            success: True if metadata scraping and updating succeeded, False otherwise
        """
        pass
    
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
    
    @staticmethod
    async def download_image(url: str, save_path: str, rename_with_serial: bool = False) -> None:
        """
        Download image from URL and save to specified path
        Args:
            url: Image URL
            save_path: Local path to save the image
            rename_with_serial: Whether to rename the file with a serial number to avoid conflicts
        """
        pass
    
