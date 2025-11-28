"""Game management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional

router = APIRouter()


@router.get("/")
async def get_games(skip: int = 0, limit: int = 100):
    """
    Get list of games
    """
    # TODO: Implement get games logic
    pass


@router.get("/{game_id}")
async def get_game(game_id: int):
    """
    Get game details by ID
    """
    # TODO: Implement get game by ID logic
    pass


@router.get("/{game_id}/manifest-hash")
async def get_game_manifest_hash(game_id: int):
    """
    Get manifest hash for quick comparison (incremental updates)
    """
    # TODO: Implement get manifest hash logic
    pass


@router.get("/{game_id}/manifest")
async def get_game_manifest(game_id: int):
    """
    Get full manifest content for detailed comparison
    """
    # TODO: Implement get manifest logic
    pass


@router.post("/scan")
async def scan_games_directory():
    """
    Trigger directory scan for new games (admin only)
    """
    # TODO: Implement directory scanning logic
    pass


@router.post("/{game_id}/scrape")
async def scrape_game_metadata(game_id: int):
    """
    Scrape metadata for a specific game from Steam/IGDB (admin only)
    """
    # TODO: Implement metadata scraping logic
    pass


@router.put("/{game_id}")
async def update_game(game_id: int):
    """
    Update game information (admin only)
    """
    # TODO: Implement update game logic
    pass
