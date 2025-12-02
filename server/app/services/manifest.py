"""Manifest management service for game indexing and comparison"""
import asyncio
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional


class ManifestService:
    """Service for managing game manifests and computing differences"""
        
    @staticmethod
    async def generate_manifest(game_id: int, game_path: Path) -> Dict:
        """
        Generate manifest.json for a game directory
        Contains file fingerprints (path, size, modified time, hash)
        
        Performance optimizations:
        - Concurrent file processing with semaphore
        - Batch hash calculations
        - Efficient file system traversal
        """
        if not game_path.exists() or not game_path.is_dir():
            raise ValueError(f"Invalid game directory: {game_path}")
        
        files = {}
        total_size = 0
        
        # Get all files recursively, excluding common non-game files
        excluded_patterns = {'.git', '__pycache__', '.DS_Store', 'Thumbs.db', '.tmp'}
        all_files = []
        
        for file_path in game_path.rglob('*'):
            if (file_path.is_file() and 
                not any(pattern in file_path.name for pattern in excluded_patterns) and
                not any(pattern in str(file_path) for pattern in excluded_patterns)):
                all_files.append(file_path)
        
        # Process files concurrently with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent file operations
        
        async def process_file(file_path: Path) -> Dict:
            """Process a single file and return its manifest entry"""
            async with semaphore:
                try:
                    # Get file stats
                    stat = file_path.stat()
                    file_size = stat.st_size
                    modified_time = stat.st_mtime
                    
                    # Calculate relative path from game directory
                    relative_path = file_path.relative_to(game_path)
                    
                    # Calculate hash
                    file_hash = await ManifestService.calculate_file_hash(file_path)
                    
                    return {
                        'path': str(relative_path).replace('\\', '/'),  # Use forward slashes
                        'size': file_size,
                        'modified_time': modified_time,
                        'hash': file_hash
                    }
                except (OSError, IOError, ValueError) as e:
                    # Log error but continue processing other files
                    print(f"Warning: Failed to process file {file_path}: {e}")
                    return None
        
        # Process all files concurrently
        tasks = [process_file(file_path) for file_path in all_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed files and calculate totals
        for result in results:
            if result is not None and not isinstance(result, Exception):
                files[result['path']] = {
                    'size': result['size'],
                    'modified_time': result['modified_time'],
                    'hash': result['hash']
                }
                total_size += result['size']
        
        # Generate manifest
        manifest = {
            'version': '1.0',
            'game_id': game_id,
            'generated_at': asyncio.get_event_loop().time(),
            'files': files,
            'total_size': total_size,
            'file_count': len(files)
        }
        
        # Save manifest to game directory
        manifest_path = game_path / 'manifest.json'
        def _save_manifest():
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        await asyncio.get_event_loop().run_in_executor(None, _save_manifest)
        
        return manifest
        
    @staticmethod
    async def calculate_file_hash(file_path: Path) -> str:
        """
        Calculate SHA-256 hash for a file using chunked async I/O
        Optimized for large files to avoid memory issues
        """
        sha256_hash = hashlib.sha256()
        chunk_size = 65536  # 64KB chunks for optimal performance
        
        try:
            # Use asyncio to run file I/O in thread pool
            def _hash_file():
                with open(file_path, 'rb') as f:
                    while chunk := f.read(chunk_size):
                        sha256_hash.update(chunk)
                return sha256_hash.hexdigest()
            
            return await asyncio.get_event_loop().run_in_executor(None, _hash_file)
        except (OSError, IOError) as e:
            raise ValueError(f"Failed to calculate hash for {file_path}: {e}")
    
    @staticmethod
    async def update_manifest(game_id: int, game_path: Path,
                              added_files: Optional[List[Path]] = None,
                              updated_files: Optional[List[Path]] = None,
                              removed_files: Optional[List[Path]] = None) -> None:
        """
        Update manifest for a specific game
        Checks for file changes and regenerates manifest if needed
        """
        manifest_path = game_path / 'manifest.json'
        
        if not manifest_path.exists():
            # No existing manifest, generate new one
            await ManifestService.generate_manifest(game_id, game_path)
            return
        
        # Load existing manifest
        def _load_manifest():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
            
        existing_manifest = await asyncio.get_event_loop().run_in_executor(None, _load_manifest)
        existing_files = existing_manifest.get('files', {})
        manifest_changed = False
        # Process removed files
        if removed_files:
            for file_path in removed_files:
                relative_path = str(file_path.relative_to(game_path)).replace('\\', '/')
                if relative_path in existing_files:
                    del existing_files[relative_path]
                    manifest_changed = True
        # Process added or updated files
        files_to_process = (added_files or []) + (updated_files or [])
        for file_path in files_to_process:
            relative_path = str(file_path.relative_to(game_path)).replace('\\', '/')
            try:
                stat = file_path.stat()
                file_size = stat.st_size
                modified_time = stat.st_mtime
                file_hash = await ManifestService.calculate_file_hash(file_path)
                
                existing_files[relative_path] = {
                    'size': file_size,
                    'modified_time': modified_time,
                    'hash': file_hash
                }
                manifest_changed = True
            except (OSError, IOError, ValueError) as e:
                print(f"Warning: Failed to process file {file_path}: {e}")
                
        if manifest_changed:
            # Recalculate totals
            total_size = sum(file_info['size'] for file_info in existing_files.values())
            file_count = len(existing_files)
            
            # Update manifest
            existing_manifest['files'] = existing_files
            existing_manifest['total_size'] = total_size
            existing_manifest['file_count'] = file_count
            existing_manifest['generated_at'] = asyncio.get_event_loop().time()
            
            # Save updated manifest
            def _save_manifest():
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_manifest, f, indent=2, ensure_ascii=False)
            
            await asyncio.get_event_loop().run_in_executor(None, _save_manifest)
    
    @staticmethod
    async def get_manifest_hash(game_path: Path) -> str:
        """
        Get quick hash of manifest for comparison
        Used for fast change detection
        """
        manifest_path = game_path / 'manifest.json'
        if not manifest_path.exists():
            return ""
        
        # Calculate hash of manifest file itself
        return await ManifestService.calculate_file_hash(manifest_path)
    

