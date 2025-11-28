# GitHub Copilot Instructions for GameVault Project

## Project Overview
GameVault is a private cloud game management platform built with Python (FastAPI) for the backend and Electron + Vue for the Windows client. The system enables game library management, automatic metadata scraping, incremental updates, and game save synchronization.

## Technology Stack

### Backend (Server)
- **Language:** Python 3.10+
- **Framework:** FastAPI (async/await with high performance)
- **Database:** SQLite with SQLAlchemy or Tortoise-ORM
- **Metadata Scraping:** BeautifulSoup4, httpx, Steam API, IGDB API
- **Background Tasks:** APScheduler (initial) or Celery (for heavy workloads)
- **File Processing:** Native Python `hashlib` and `os` modules

### Frontend (Client)
- **Shell:** Electron (targeting Windows, cross-platform ready)
- **UI Framework:** Vue 3 or React
- **Main Process:** Node.js with `fs`, `crypto` modules
- **Download Library:** Got or Axios (streaming support)
- **Process Management:** `child_process` for launching games

## Project Structure

```
/gamevault-root
  ├── /server                 # Python FastAPI backend
  │    ├── /app
  │    │    ├── /api          # REST API endpoints
  │    │    ├── /core         # Core configuration
  │    │    ├── /crud         # Database CRUD operations
  │    │    ├── /models       # Database models
  │    │    ├── /schemas      # Pydantic validation schemas
  │    │    ├── /services     # Business logic (Scanner, Scraper, Hashing)
  │    │    └── main.py       # Application entry point
  │    ├── /storage           # Game storage directory
  │    └── requirements.txt
  │
  └── /client                 # Electron + Vue frontend
       ├── /src
       │    ├── /main         # Electron main process (file handling, download logic)
       │    ├── /renderer     # Vue UI code
       │    └── /common       # Shared types and utilities
       ├── package.json
       └── electron-builder.yml
```

## Core Features & Implementation Guidance

### 1. Server-Side Directory Scanning & Metadata Scraping
When implementing directory scanning features:
- Use Python's async capabilities with FastAPI
- Parse folder names to identify games (e.g., "The Witcher 3")
- Query Steam API or IGDB API for game metadata
- Store cover images in `/storage/static/images`
- Save game information (GameID, SteamID, IGDBID, description, developer etc.) to SQLite
- Generate `manifest.json` for each game with file fingerprints (path, size, modified time, hash)

### 2. Incremental Updates (Critical Feature)
**Server Side (Python):**
- Monitor game directory changes and update `manifest.json`
- Provide endpoint `GET /api/games/{id}/manifest-hash` for quick comparison
- Provide endpoint `GET /api/games/{id}/manifest` for full manifest content

**Client Side (Electron Main Process):**
- Step 1: Compare manifest hashes (local vs. server)
- Step 2: Perform detailed diff on manifest content to identify new, modified, deleted files
- Step 3: Generate download/overwrite and deletion task lists
- Step 4: Implement resumable downloads using `fs.createWriteStream` and HTTP Range requests

### 3. Game Save Synchronization
**Python Backend:**
- Accept uploaded save files from clients
- Store save file paths with game IDs in database
- Support versioning (keep multiple save versions)

**Electron Client:**
- Use `child_process` to launch game executables
- Monitor process exit events to trigger save sync
- Use `archiver` library to zip save directories
- Upload to server and display save history in UI

### 4. Multi-User Management
- Implement JWT authentication using FastAPI Users library or custom implementation
- Store JWT tokens in `electron-store` for persistence
- Include tokens in API request headers

### 5. Storage
- All data store in to `/storage` by default, can be configured by admin
- SQLite file located at `/storage/gamevault.db`
- Game cover images in `/storage/static/images`
- User save files organized by user ID and game ID `/storage/saves/{user_id}/{game_id}/`

### 6. Administration Interface
- Generate a administration account on first run
- Login on the client to access admin features (admin panel)
- Admin can configure game directories, view logs, manage users games, etc.

## Coding Standards & Conventions

### Python (Backend)
- Use async/await patterns with FastAPI
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Organize code into clear separation: API routes, business logic (services), and data access (CRUD)
- Use Pydantic models for request/response validation
- Handle errors with appropriate HTTP status codes

### JavaScript/TypeScript (Frontend)
- Use async/await for asynchronous operations
- Separate Electron main process logic from renderer process
- Use IPC (Inter-Process Communication) for main-renderer communication
- Follow Vue 3 Composition API patterns
- Handle file I/O operations in main process only (not renderer)

### Database
- Use SQLAlchemy ORM patterns
- Create proper indexes for frequently queried fields
- Use migrations for schema changes
- Store file hashes for integrity verification

### API Design
- Follow RESTful conventions
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Version APIs when necessary (e.g., `/api/v1/`)
- Return consistent error response formats
- Generate automatic OpenAPI documentation with FastAPI

## Key Implementation Notes

### File Hashing & Integrity
- Use SHA-256 for file hashing
- Store hashes in manifest.json for each file
- Implement chunk-based hashing for large files to avoid memory issues

### Download Optimization
- Implement multi-threaded downloads
- Support resumable downloads with Range requests
- Show progress updates in UI
- Handle network errors gracefully with retry logic

### Performance Considerations
- Use streaming for large file transfers
- Implement caching for metadata and images
- Use background tasks for heavy operations (scanning, scraping)
- Optimize database queries with proper indexing

### Security
- Validate all user inputs with Pydantic
- Implement proper JWT token expiration
- Use HTTPS for production deployments
- Sanitize file paths to prevent directory traversal attacks
- Implement rate limiting for API endpoints

## Development Workflow

### Phase 1: MVP
- Basic FastAPI server with directory scanning
- Electron + Vue shell with login and game list UI
- Simple full-download functionality (no incremental updates yet)

### Phase 2: Metadata & UI Polish
- Steam API integration for cover art and metadata
- Beautiful poster wall interface
- Download progress indicators
- User registration and admin panel

### Phase 3: Incremental Updates (Most Complex)
- Generate manifest.json with file hashes
- Implement resumable downloads
- Client-side integrity verification and repair

### Phase 4: Save Sync & Advanced Features
- Game launcher functionality
- Automatic save backup on game exit
- User permission controls and access management

## When Writing Code

### For Python/FastAPI:
- Prefer async route handlers
- Use dependency injection for database sessions
- Implement proper logging with Python's logging module
- Write unit tests for business logic

### For Electron:
- Keep heavy I/O operations in main process
- Use IPC for communication between main and renderer
- Implement proper error handling and user notifications
- Store configuration in electron-store

### For File Operations:
- Always use absolute paths
- Handle file system errors gracefully
- Implement proper cleanup for temporary files
- Use streams for large file operations

## Common Patterns

### API Endpoint Pattern:
```python
@router.get("/games/{game_id}/manifest")
async def get_game_manifest(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementation
```

### Electron IPC Pattern:
```javascript
// Main process
ipcMain.handle('download-game', async (event, gameId) => {
    // Implementation
});

// Renderer process
const result = await ipcRenderer.invoke('download-game', gameId);
```

### File Hashing Pattern:
```python
def calculate_file_hash(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
```

## Testing Considerations
- Write unit tests for Python business logic
- Test API endpoints with TestClient from FastAPI
- Test Electron main process logic separately from renderer
- Mock external API calls (Steam, IGDB) in tests
- Test file operations with temporary directories

## Deployment Notes
- Use electron-builder for packaging Windows client
- Include Python runtime with PyInstaller or similar if needed
- Configure proper file paths for production vs. development
- Document environment variables and configuration files
