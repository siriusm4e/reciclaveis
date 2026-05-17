import { api } from '@/api/client';
import type { ConteudoEducativo, ID, PreferenciaComunicacao } from '@/types/api';

export const conteudoApi = {
  list: (params: { papel?: string; categoria?: string; page?: number; page_size?: number } = {}) =>
    api.get<ConteudoEducativo[]>('/conteudo/', { params }).then((r) => r.data),
  get: (id: ID) => api.get<ConteudoEducativo>(`/conteudo/${id}`).then((r) => r.data),
};

export const preferenciasApi = {
  get: () => api.get<PreferenciaComunicacao>('/preferencias-comunicacao/').then((r) => r.data),
  update: (payload: Partial<PreferenciaComunicacao>) =>
    api.patch<PreferenciaComunicacao>('/preferencias-comunicacao/', payload).then((r) => r.data),
};

export const dispositivosApi = {
  registrar: (payload: {
    plataforma: 'ios' | 'android' | 'web';
    token: string;
    modelo?: string;
    versao_app?: string;
  }) => api.post('/dispositivos/token', payload).then((r) => r.data),
};
