import axios from 'axios';
import type {
  User,
  MatchCreate,
  MatchResponse,
  AnalyzeResponse,
  OverallStats,
  SurvivorPickStats,
  SurvivorWinrateStats,
  SurvivorKiteStats,
  MapStats,
  LoginResponse,
  TokenResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（トークン付与）
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// レスポンスインターセプター（トークンリフレッシュ）
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // トークン期限切れの場合はログアウト
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// 認証API
export const authApi = {
  login: async (redirectUrl?: string): Promise<LoginResponse> => {
    const { data } = await api.post('/auth/login', { redirect_url: redirectUrl });
    return data;
  },

  exchangeToken: async (code: string): Promise<TokenResponse> => {
    const { data } = await api.post('/auth/token', { code });
    return data;
  },

  getMe: async (): Promise<User> => {
    const { data } = await api.get('/auth/me');
    return data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// 試合API
export const matchesApi = {
  analyze: async (file: File): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/api/matches/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // OCRは時間がかかるので60秒
    });
    return data;
  },

  create: async (match: MatchCreate): Promise<MatchResponse> => {
    const { data } = await api.post('/api/matches', match);
    return data;
  },

  getAll: async (params?: {
    hunter?: string;
    trait?: string;
    map_name?: string;
    persona?: string;
    result?: string;
    limit?: number;
  }): Promise<{ matches: MatchResponse[]; total: number }> => {
    const { data } = await api.get('/api/matches', { params });
    return data;
  },

  get: async (id: number): Promise<MatchResponse> => {
    const { data } = await api.get(`/api/matches/${id}`);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/matches/${id}`);
  },
};

// 統計API
export const statsApi = {
  getOverall: async (hunter?: string, trait?: string, persona?: string, bannedCharacters?: string[]): Promise<OverallStats> => {
    const params: any = { hunter, trait, persona };
    if (bannedCharacters && bannedCharacters.length > 0) {
      params.banned_characters = bannedCharacters.join(',');
    }
    const { data } = await api.get('/api/stats/overall', { params });
    return data;
  },

  getSurvivorPicks: async (hunter?: string, trait?: string, limit?: number, persona?: string, bannedCharacters?: string[]): Promise<SurvivorPickStats[]> => {
    const params: any = { hunter, trait, limit, persona };
    if (bannedCharacters && bannedCharacters.length > 0) {
      params.banned_characters = bannedCharacters.join(',');
    }
    const { data } = await api.get('/api/stats/survivors/picks', { params });
    return data;
  },

  getSurvivorWinrate: async (hunter?: string, trait?: string, limit?: number, persona?: string, bannedCharacters?: string[]): Promise<SurvivorWinrateStats[]> => {
    const params: any = { hunter, trait, limit, persona };
    if (bannedCharacters && bannedCharacters.length > 0) {
      params.banned_characters = bannedCharacters.join(',');
    }
    const { data } = await api.get('/api/stats/survivors/winrate', { params });
    return data;
  },

  getSurvivorKite: async (hunter?: string, trait?: string, limit?: number, persona?: string, bannedCharacters?: string[]): Promise<SurvivorKiteStats[]> => {
    const params: any = { hunter, trait, limit, persona };
    if (bannedCharacters && bannedCharacters.length > 0) {
      params.banned_characters = bannedCharacters.join(',');
    }
    const { data } = await api.get('/api/stats/survivors/kite', { params });
    return data;
  },

  getMapStats: async (hunter?: string, trait?: string, limit?: number, persona?: string, bannedCharacters?: string[]): Promise<MapStats[]> => {
    const params: any = { hunter, trait, limit, persona };
    if (bannedCharacters && bannedCharacters.length > 0) {
      params.banned_characters = bannedCharacters.join(',');
    }
    const { data } = await api.get('/api/stats/maps', { params });
    return data;
  },

  getRecentPersonas: async (): Promise<string[]> => {
    const { data } = await api.get('/api/stats/personas');
    return data;
  },
};

// マスターデータAPI
export const masterApi = {
  getHunters: async (): Promise<string[]> => {
    const { data } = await api.get('/api/master/hunters');
    return data;
  },

  getSurvivors: async (): Promise<string[]> => {
    const { data } = await api.get('/api/master/survivors');
    return data;
  },

  getTraits: async (): Promise<string[]> => {
    const { data } = await api.get('/api/master/traits');
    return data;
  },

  getMaps: async (): Promise<string[]> => {
    const { data } = await api.get('/api/master/maps');
    return data;
  },
};

export default api;
