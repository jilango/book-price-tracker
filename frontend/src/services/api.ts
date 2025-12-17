/** API client for backend communication. */

import axios from 'axios';
import type {
  Book,
  BookListResponse,
  PriceHistory,
  Alert,
  AlertListResponse,
  DashboardStats,
  PriceTrendsResponse,
  ComparisonStats,
  SyncStatus,
  SyncHistoryListResponse,
  PriceDistributionResponse,
  DataQualityResponse,
  RecentActivityResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Books API
export const booksAPI = {
  list: async (params?: {
    search?: string;
    sort?: string;
    order?: string;
    page?: number;
    limit?: number;
    alert_only?: boolean;
  }): Promise<BookListResponse> => {
    const response = await api.get<BookListResponse>('/api/books', { params });
    return response.data;
  },

  getByISBN: async (isbn: string): Promise<Book> => {
    const response = await api.get<Book>(`/api/books/${isbn}`);
    return response.data;
  },

  getPriceHistory: async (bookId: number, limit = 100): Promise<PriceHistory[]> => {
    const response = await api.get<PriceHistory[]>(`/api/books/${bookId}/price-history`, {
      params: { limit },
    });
    return response.data;
  },
};

// Alerts API
export const alertsAPI = {
  list: async (params?: {
    status?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    limit?: number;
  }): Promise<AlertListResponse> => {
    const response = await api.get<AlertListResponse>('/api/alerts', { params });
    return response.data;
  },

  getActive: async (page = 1, limit = 50): Promise<AlertListResponse> => {
    const response = await api.get<AlertListResponse>('/api/alerts/active', {
      params: { page, limit },
    });
    return response.data;
  },

  get: async (alertId: number): Promise<Alert> => {
    const response = await api.get<Alert>(`/api/alerts/${alertId}`);
    return response.data;
  },

  acknowledge: async (alertId: number): Promise<Alert> => {
    const response = await api.post<Alert>(`/api/alerts/${alertId}/acknowledge`);
    return response.data;
  },
};

// Statistics API
export const statsAPI = {
  getDashboard: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/api/stats/dashboard');
    return response.data;
  },

  getPriceTrends: async (days = 30, bookId?: number): Promise<PriceTrendsResponse> => {
    const response = await api.get<PriceTrendsResponse>('/api/stats/price-trends', {
      params: { days, book_id: bookId },
    });
    return response.data;
  },

  getComparison: async (): Promise<ComparisonStats> => {
    const response = await api.get<ComparisonStats>('/api/stats/comparison');
    return response.data;
  },

  getPriceDistribution: async (): Promise<PriceDistributionResponse> => {
    const response = await api.get<PriceDistributionResponse>('/api/stats/price-distribution');
    return response.data;
  },

  getDataQuality: async (): Promise<DataQualityResponse> => {
    const response = await api.get<DataQualityResponse>('/api/stats/data-quality');
    return response.data;
  },

  getRecentActivity: async (days = 30): Promise<RecentActivityResponse> => {
    const response = await api.get<RecentActivityResponse>('/api/stats/recent-activity', {
      params: { days },
    });
    return response.data;
  },
};

// Sync API
export const syncAPI = {
  getStatus: async (): Promise<SyncStatus> => {
    const response = await api.get<SyncStatus>('/api/sync/status');
    return response.data;
  },

  getHistory: async (limit = 50): Promise<SyncHistoryListResponse> => {
    const response = await api.get<SyncHistoryListResponse>('/api/sync/history', {
      params: { limit },
    });
    return response.data;
  },
};

export default api;

