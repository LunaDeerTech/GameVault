# GameVault Client

Electron + Vue 3 desktop client for GameVault private cloud game management platform.

## Features

- Beautiful game library interface with poster wall
- Incremental game updates with resume support
- Game launcher with automatic save synchronization
- User authentication and profile management
- Download progress tracking
- Offline game access

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run in development mode:
```bash
npm run electron:dev
```

3. Build for production:
```bash
npm run electron:build
```

## Project Structure

```
client/
├── src/
│   ├── main/           # Electron main process
│   │   ├── index.ts    # Main entry point
│   │   └── preload.ts  # IPC bridge
│   ├── renderer/       # Vue application
│   │   ├── components/ # Reusable components
│   │   ├── views/      # Page views
│   │   ├── store/      # Pinia state management
│   │   └── assets/     # Static assets
│   └── common/         # Shared types and utilities
├── package.json
└── vite.config.ts
```

## Development

### Available Scripts

- `npm run dev` - Start Vite dev server
- `npm run electron:dev` - Start Electron in development mode
- `npm run build` - Build for production
- `npm run electron:build` - Build Electron installer
- `npm run lint` - Lint code

### IPC Communication

The main process exposes safe APIs to the renderer through the preload script:

```typescript
// In renderer
const result = await window.electron.downloadGame(gameId);
```

Available APIs:
- `getAppVersion()` - Get app version
- `store.get(key)` / `store.set(key, value)` - Persistent storage
- `downloadGame(gameId)` - Download/update game
- `launchGame(gamePath)` - Launch game executable
- `uploadSave(gameId, savePath)` - Upload save to server
- `downloadSave(gameId, saveId)` - Download save from server

## Tech Stack

- **Electron** - Desktop application framework
- **Vue 3** - Progressive JavaScript framework
- **Pinia** - State management
- **Vue Router** - Routing
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Axios** - HTTP client
- **Archiver** - File compression for saves

## Building

Windows installer will be generated in `release/` directory:
```bash
npm run electron:build
```

## Configuration

Server URL can be configured in `src/common/api.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000';
```
