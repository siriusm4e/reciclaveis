import { api } from '@/api/client';
import type { TokenPair, UsuarioPublic } from '@/types/api';

export interface RegisterPayload {
  cpf: string;
  email: string;
  senha: string;
  nome_completo: string;
  telefone?: string;
}

export interface LoginPayload {
  email: string;
  senha: string;
  mfa_code?: string;
}

export const authApi = {
  register: (p: RegisterPayload) => api.post<UsuarioPublic>('/auth/register', p).then((r) => r.data),
  login: (p: LoginPayload) => api.post<TokenPair>('/auth/login', p).then((r) => r.data),
  refresh: (refresh_token: string) =>
    api.post<TokenPair>('/auth/refresh', { refresh_token }).then((r) => r.data),
  logout: (refresh_token: string) => api.post('/auth/logout', { refresh_token }),
  me: () => api.get<UsuarioPublic>('/auth/me').then((r) => r.data),
  mfaSetup: () =>
    api.post<{ secret: string; otpauth_uri: string }>('/auth/mfa/setup').then((r) => r.data),
  mfaVerify: (code: string) => api.post('/auth/mfa/verify', { code }),
  getConvite: (token: string) => api.get(`/auth/convites/${token}`).then((r) => r.data),
  aceitarConvite: (token: string) =>
    api.post(`/auth/convites/${token}/aceitar`, { token }).then((r) => r.data),
};
