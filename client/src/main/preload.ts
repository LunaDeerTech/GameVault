/**
 * Electron Preload Script
 * Exposes safe IPC methods to renderer process
 */
import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Store operations
  store: {
    get: (key: string) => ipcRenderer.invoke('store-get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('store-set', key, value),
  },

  // Game operations
  downloadGame: (gameId: number) => ipcRenderer.invoke('download-game', gameId),
  launchGame: (gamePath: string) => ipcRenderer.invoke('launch-game', gamePath),

  // Save operations
  uploadSave: (gameId: number, savePath: string) => 
    ipcRenderer.invoke('upload-save', gameId, savePath),
  downloadSave: (gameId: number, saveId: number) => 
    ipcRenderer.invoke('download-save', gameId, saveId),
});

// Type definitions for window.electron
export interface IElectronAPI {
  getAppVersion: () => Promise<string>;
  store: {
    get: (key: string) => Promise<any>;
    set: (key: string, value: any) => Promise<boolean>;
  };
  downloadGame: (gameId: number) => Promise<{ success: boolean; message?: string }>;
  launchGame: (gamePath: string) => Promise<{ success: boolean; message?: string }>;
  uploadSave: (gameId: number, savePath: string) => Promise<{ success: boolean; message?: string }>;
  downloadSave: (gameId: number, saveId: number) => Promise<{ success: boolean; message?: string }>;
}

declare global {
  interface Window {
    electron: IElectronAPI;
  }
}
