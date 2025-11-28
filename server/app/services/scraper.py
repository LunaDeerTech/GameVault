"""Metadata scraping service from Steam/IGDB"""
import httpx
from typing import Optional, Dict


class MetadataScraper:
    """Service for scraping game metadata from external APIs"""
    
    def __init__(self, steam_api_key: str = "", igdb_client_id: str = "", igdb_client_secret: str = ""):
        self.steam_api_key = steam_api_key
        self.igdb_client_id = igdb_client_id
        self.igdb_client_secret = igdb_client_secret
    
    async def search_steam(self, game_name: str) -> Optional[Dict]:
        """
        Search for game on Steam by name
        Returns game metadata including AppID, description, developer, cover art URL
        """
        # TODO: Implement Steam API search
        pass
    
    async def search_igdb(self, game_name: str) -> Optional[Dict]:
        """
        Search for game on IGDB by name
        Returns game metadata
        """
        # TODO: Implement IGDB API search
        pass
    
    async def download_cover_image(self, image_url: str, save_path: str) -> str:
        """
        Download cover image from URL and save to local storage
        Returns local file path
        """
        # TODO: Implement image download
        pass
