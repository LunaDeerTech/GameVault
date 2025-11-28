/**
 * Electron Main Process
 * Handles file operations, downloads, and IPC communication
 */
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import Store from 'electron-store';

const store = new Store();

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('store-get', (event, key: string) => {
  return store.get(key);
});

ipcMain.handle('store-set', (event, key: string, value: any) => {
  store.set(key, value);
  return true;
});

ipcMain.handle('download-game', async (event, gameId: number) => {
  // TODO: Implement game download logic
  // - Compare manifests
  // - Calculate file differences
  // - Download missing/modified files with resume support
  // - Verify file integrity
  return { success: false, message: 'Not implemented' };
});

ipcMain.handle('launch-game', async (event, gamePath: string) => {
  // TODO: Implement game launcher
  // - Launch game executable using child_process
  // - Monitor game process
  // - Trigger save sync on game exit
  return { success: false, message: 'Not implemented' };
});

ipcMain.handle('upload-save', async (event, gameId: number, savePath: string) => {
  // TODO: Implement save upload
  // - Zip save directory using archiver
  // - Upload to server
  return { success: false, message: 'Not implemented' };
});

ipcMain.handle('download-save', async (event, gameId: number, saveId: number) => {
  // TODO: Implement save download
  // - Download save file from server
  // - Extract to local save directory
  return { success: false, message: 'Not implemented' };
});
