"""Manifest Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class FileManifestEntry(BaseModel):
    """Schema for a single file in manifest"""
    path: str = Field(..., description="Relative file path")
    size: int = Field(..., description="File size in bytes", ge=0)
    modified_time: datetime = Field(..., description="Last modified time")
    hash: str = Field(..., description="SHA-256 hash of the file")


class GameManifest(BaseModel):
    """Schema for game manifest (for incremental updates)"""
    game_id: int = Field(..., description="ID of the game")
    version: str = Field(..., description="Version of the manifest")
    files: List[FileManifestEntry] = Field(..., description="List of files in the manifest")
    total_size: int = Field(..., description="Total size of all files in bytes", ge=0)
    file_count: int = Field(..., description="Total number of files in the manifest")