"""FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
import logging, os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api import games, users, auth, saves
from app.services.scraper import metadataScraperService
from app.services.scanner import initialScannerService
from app.services.watchdog import GameWatchdogService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

logger.info("Initializing storage...")
if not os.path.exists(settings.STORAGE_PATH):
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    logger.info(f"Created storage directory at {settings.STORAGE_PATH}")
    os.makedirs(os.path.join(settings.STORAGE_PATH, "static"), exist_ok=True)
    logger.info(f"Created static directory at {os.path.join(settings.STORAGE_PATH, 'static')}")
    os.makedirs(os.path.join(settings.STORAGE_PATH, "saves"), exist_ok=True)
    logger.info(f"Created saves directory at {os.path.join(settings.STORAGE_PATH, 'saves')}")
else:
    logger.info(f"Storage directory already exists at {settings.STORAGE_PATH}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    from app.core.database import init_db
    
    logger = logging.getLogger(__name__)
    
    # Startup: Initialize application
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    metadataScraperService.start(
        igdb_client_id=settings.IGDB_CLIENT_ID,
        igdb_client_secret=settings.IGDB_CLIENT_SECRET,
        max_workers=5
    )
    initialScannerService.start(max_concurrent_scans=5)
    
    watchdog_services = []
    for path in settings.GAME_CONTENT_PATHS:
        try:
            watchdog = GameWatchdogService(Path(path))
            await watchdog.start_monitoring()
            watchdog_services.append(watchdog)
            logger.info(f"Started GameWatchdogService for path: {path}")
        except Exception as e:
            logger.error(f"Failed to start GameWatchdogService for path {path}: {e}")
    
    yield
    
    # Shutdown: Cleanup
    for watchdog in watchdog_services:
        await watchdog.stop_monitoring()
    await metadataScraperService.stop()
    await initialScannerService.stop()
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GameVault Private Cloud Game Management Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="storage/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(saves.router, prefix="/api/saves", tags=["saves"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GameVault API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
