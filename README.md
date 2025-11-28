# GameVault

Private cloud game management platform for managing your game library with automatic metadata scraping, incremental updates, and save synchronization.

## Project Structure

```
GameVault/
├── server/          # Python FastAPI backend
│   ├── app/         # Application code
│   ├── storage/     # Data storage
│   └── README.md
│
├── client/          # Electron + Vue frontend
│   ├── src/         # Source code
│   └── README.md
│
└── .github/
    └── copilot-instructions.md
```

## Features

### Backend (Server)
- 🎮 Automatic game directory scanning and metadata scraping
- 📊 Steam and IGDB API integration for game information
- 🔄 Incremental update system with file manifests
- 💾 Game save synchronization and versioning
- 🔐 User authentication with JWT
- 📡 RESTful API with automatic documentation

### Frontend (Client)
- 🖼️ Beautiful poster wall interface for game library
- ⬇️ Smart download manager with resume support
- 🎯 Incremental updates - only download changed files
- 🚀 One-click game launcher
- ☁️ Automatic save backup and restore
- 👤 User profile and settings management

## Quick Start

### Server Setup

1. Navigate to server directory:
```bash
cd server
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Configure environment:
```bash
copy config.yaml.example config.yaml
# Edit config.yaml with your configuration
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Client Setup

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Run in development mode:
```bash
npm run electron:dev
```

4. Build for production:
```bash
npm run electron:build
```

## Technology Stack

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- BeautifulSoup4 for web scraping
- APScheduler for background tasks

**Frontend:**
- Electron
- Vue 3
- TypeScript
- Pinia (state management)
- Axios (HTTP client)

## Development Roadmap

### Phase 1: MVP ✅
- [x] Basic server structure
- [x] Basic client structure
- [ ] Simple file download functionality
- [ ] User authentication

### Phase 2: Metadata & UI
- [ ] Steam API integration
- [ ] Game metadata scraping
- [ ] Poster wall interface
- [ ] Download progress tracking

### Phase 3: Incremental Updates
- [ ] Manifest generation
- [ ] File diff calculation
- [ ] Resumable downloads
- [ ] Integrity verification

### Phase 4: Advanced Features
- [ ] Game launcher
- [ ] Save synchronization
- [ ] Multi-user permissions
- [ ] Download queue management

## Documentation

- [Server Documentation](server/README.md)
- [Client Documentation](client/README.md)
- [GitHub Copilot Instructions](.github/copilot-instructions.md)

## License

MIT

## Contributing

This is a private project. Contributions are welcome from authorized team members.

## Support

For issues and questions, please contact the development team.
