import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios';

import { useAuthStore } from '@/store/authStore';
import { useContaStore } from '@/store/contaStore';
import type { ApiError } from '@/types/api';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const api: AxiosInstance = axios.create({
  baseURL: BASE_URL.replace(/\/$/, ''),
  timeout: 30_000,
});

// ===== Interceptor de request: injeta Authorization + X-Conta-Id =====
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`);
  }
  const { contaAtivaId } = useContaStore.getState();
  if (contaAtivaId) {
    config.headers.set('X-Conta-Id', contaAtivaId);
  }
  return config;
});

// ===== Refresh em 401 =====

let refreshPromise: Promise<string | null> | null = null;

async function tryRefresh(): Promise<string | null> {
  const { refreshToken, setTokens, clear } = useAuthStore.getState();
  if (!refreshToken) {
    clear();
    return null;
  }
  try {
    const { data } = await axios.post(`${BASE_URL.replace(/\/$/, '')}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    setTokens(data);
    return data.access_token;
  } catch {
    clear();
    return null;
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;

    if (status === 401 && original && !original._retry) {
      original._retry = true;
      if (!refreshPromise) refreshPromise = tryRefresh();
      const newToken = await refreshPromise;
      refreshPromise = null;
      if (newToken) {
        original.headers = { ...(original.headers || {}), Authorization: `Bearer ${newToken}` };
        return api.request(original);
      }
      // Redireciona para login
      if (typeof window !== 'undefined') {
        window.location.assign('/auth/login');
      }
    }
    return Promise.reject(error);
  },
);

// ===== Helper para extrair mensagem amigável =====

export function extractErrorMessage(err: unknown, fallback = 'Erro inesperado'): string {
  if (axios.isAxiosError<ApiError>(err)) {
    return err.response?.data?.error?.message || err.message || fallback;
  }
  if (err instanceof Error) return err.message;
  return fallback;
}
