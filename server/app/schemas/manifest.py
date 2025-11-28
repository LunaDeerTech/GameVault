"""Manifest Pydantic schemas"""
from pydantic import BaseModel
from typing import List
from datetime import datetime


class FileManifestEntry(BaseModel):
    """Schema for a single file in manifest"""
    path: str
    size: int
    modified_time: datetime
    hash: str  # SHA-256


class GameManifest(BaseModel):
    """Schema for game manifest (for incremental updates)"""
    game_id: int
    version: str  # e.g. timestamp or hash
    files: List[FileManifestEntry]
    total_size: int
    file_count: int
