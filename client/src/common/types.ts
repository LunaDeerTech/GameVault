/**
 * Common type definitions
 */

export interface User {
  id: number;
  username: string;
  email: string;
  isAdmin: boolean;
}

export interface Game {
  id: number;
  name: string;
  description: string;
  developer: string;
  publisher: string;
  coverImage: string;
  steamId?: string;
  igdbId?: string;
  totalSize: number;
  fileCount: number;
}

export interface GameManifest {
  version: string;
  gameId: number;
  files: FileManifestEntry[];
  manifestHash: string;
}

export interface FileManifestEntry {
  path: string;
  size: number;
  modifiedTime: string;
  hash: string;
}

export interface GameSave {
  id: number;
  gameId: number;
  userId: number;
  filePath: string;
  fileSize: number;
  version: number;
  description?: string;
  createdAt: string;
}

export interface DownloadProgress {
  gameId: number;
  totalFiles: number;
  completedFiles: number;
  totalBytes: number;
  downloadedBytes: number;
  speed: number;
  eta: number;
}
