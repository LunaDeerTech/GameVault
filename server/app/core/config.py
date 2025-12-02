"""Application Configuration"""
from datetime import timezone
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, validator
import time
from datetime import timedelta


def load_config_yaml(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    # If config.yaml doesn't exist, try config.yaml.example
    if not config_file.exists():
        example_config = Path("config.yaml.example")
        if example_config.exists():
            print(f"Warning: {config_path} not found, using {example_config}")
            config_file = example_config
        else:
            raise FileNotFoundError(f"Configuration file {config_path} not found")
    
    with open(config_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


class Settings(BaseModel):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "GameVault"
    VERSION: str = "0.1.0"
    
    # Game content paths
    GAME_CONTENT_PATHS: List[str] = ["/games"]
    
    # Environment
    ENVIRONMENT: str = "production"  # "development" or "production"
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "sqlite:///storage/gamevault.db"
    
    # Storage
    STORAGE_PATH: str = "/storage"
    
    # External APIs
    IGDB_CLIENT_ID: str = ""
    IGDB_CLIENT_SECRET: str = ""
    
    # Timezone - auto-detected from system
    TZ: timezone = timezone.utc
    
    @validator('TZ', pre=True, always=True)
    def set_timezone(cls, v):
        """Auto-detect system timezone, fallback to UTC"""
        try:
            # Get local timezone offset in seconds
            if time.daylight:
                offset_seconds = -time.altzone
            else:
                offset_seconds = -time.timezone
            
            # Create timezone object with offset
            return timezone(timedelta(seconds=offset_seconds))
        except Exception:
            # Fallback to UTC if detection fails
            return timezone.utc
    
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def from_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """Create Settings instance from YAML configuration"""
        config_data = load_config_yaml(config_path)
        
        # Map YAML structure to flat settings
        settings_data = {
            "ENVIRONMENT": config_data.get("environment", "production"),
            "LOG_LEVEL": config_data.get("logging", {}).get("level", "INFO"),
            "GAME_CONTENT_PATHS": config_data.get("game-content-paths", ["/games"]),
            "SECRET_KEY": config_data.get("security", {}).get("secret_key", "your-secret-key-here-change-in-production"),
            "ALGORITHM": config_data.get("security", {}).get("algorithm", "HS256"),
            "ACCESS_TOKEN_EXPIRE_MINUTES": config_data.get("security", {}).get("access_token_expire_minutes", 10080),
            "ALLOWED_ORIGINS": config_data.get("cors-allowed_origins", ["http://localhost:3000", "http://localhost:5173"]),
            "DATABASE_URL": config_data.get("database-url", "sqlite:///storage/gamevault.db"),
            "STORAGE_PATH": config_data.get("storage-path", "/storage"),
            "IGDB_CLIENT_ID": config_data.get("igdb", {}).get("client_id", ""),
            "IGDB_CLIENT_SECRET": config_data.get("igdb", {}).get("client_secret", ""),
        }
        
        return cls(**settings_data)


settings = Settings.from_yaml()
