"""FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api import games, users, auth, saves


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    from app.core.database import init_db
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Startup: Initialize application
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # TODO: Start background tasks (APScheduler)
    
    yield
    
    # Shutdown: Cleanup
    # TODO: Close database connections
    # TODO: Stop background tasks
    pass


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
