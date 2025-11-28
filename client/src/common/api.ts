/**
 * API client for communicating with GameVault server
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });

    // Add request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      // TODO: Get token from electron-store
      const token = null;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Auth endpoints
  async login(username: string, password: string) {
    // TODO: Implement login
    return this.client.post('/api/auth/token', { username, password });
  }

  async register(username: string, email: string, password: string) {
    // TODO: Implement registration
    return this.client.post('/api/auth/register', { username, email, password });
  }

  // Game endpoints
  async getGames() {
    // TODO: Implement get games
    return this.client.get('/api/games');
  }

  async getGame(id: number) {
    // TODO: Implement get game
    return this.client.get(`/api/games/${id}`);
  }

  async getGameManifestHash(id: number) {
    // TODO: Implement get manifest hash
    return this.client.get(`/api/games/${id}/manifest-hash`);
  }

  async getGameManifest(id: number) {
    // TODO: Implement get manifest
    return this.client.get(`/api/games/${id}/manifest`);
  }

  // Save endpoints
  async getGameSaves(gameId: number) {
    // TODO: Implement get saves
    return this.client.get(`/api/saves/${gameId}`);
  }

  async uploadSave(gameId: number, file: File) {
    // TODO: Implement upload save
    const formData = new FormData();
    formData.append('file', file);
    return this.client.post(`/api/saves/${gameId}/upload`, formData);
  }

  async downloadSave(gameId: number, saveId: number) {
    // TODO: Implement download save
    return this.client.get(`/api/saves/${gameId}/download/${saveId}`, {
      responseType: 'blob',
    });
  }
}

export const apiClient = new ApiClient();
