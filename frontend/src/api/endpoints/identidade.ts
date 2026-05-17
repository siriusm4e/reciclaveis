import { api } from '@/api/client';
import type {
  Conta,
  ContaTipo,
  Estabelecimento,
  ID,
  Membro,
  Papel,
  PapelInternoMembro,
  PapelStatus,
  PapelTipo,
} from '@/types/api';

export const contasApi = {
  list: () => api.get<Conta[]>('/contas/').then((r) => r.data),
  get: (id: ID) => api.get<Conta>(`/contas/${id}`).then((r) => r.data),
  create: (p: {
    tipo: ContaTipo;
    nome_publico: string;
    cnpj?: string;
    escopo_territorial?: Record<string, unknown>;
  }) => api.post<Conta>('/contas/', p).then((r) => r.data),
  update: (id: ID, p: Partial<Conta>) => api.patch<Conta>(`/contas/${id}`, p).then((r) => r.data),
};

export const membrosApi = {
  list: (contaId: ID) =>
    api.get<Membro[]>(`/contas/${contaId}/membros/`).then((r) => r.data),
  convidar: (contaId: ID, email: string, papel_interno: PapelInternoMembro = 'operador') =>
    api
      .post(`/contas/${contaId}/membros/`, { email, papel_interno })
      .then((r) => r.data),
  remover: (contaId: ID, membroId: ID) =>
    api.delete(`/contas/${contaId}/membros/${membroId}`).then((r) => r.data),
};

export const papeisApi = {
  list: (contaId: ID) => api.get<Papel[]>(`/contas/${contaId}/papeis/`).then((r) => r.data),
  ativar: (contaId: ID, papel: PapelTipo, dados_complementares: Record<string, unknown> = {}) =>
    api
      .post<Papel>(`/contas/${contaId}/papeis/`, { papel, dados_complementares })
      .then((r) => r.data),
  atualizar: (
    contaId: ID,
    papelId: ID,
    payload: { dados_complementares?: Record<string, unknown>; status?: PapelStatus },
  ) => api.patch<Papel>(`/contas/${contaId}/papeis/${papelId}`, payload).then((r) => r.data),
};

export const estabelecimentosApi = {
  list: (contaId: ID) =>
    api.get<Estabelecimento[]>(`/contas/${contaId}/estabelecimentos/`).then((r) => r.data),
  criar: (
    contaId: ID,
    payload: {
      nome: string;
      cep: string;
      logradouro: string;
      numero: string;
      complemento?: string;
      bairro: string;
      cidade: string;
      uf: string;
      ibge_municipio?: string;
      localizacao: { lat: number; lng: number };
    },
  ) =>
    api
      .post<Estabelecimento>(`/contas/${contaId}/estabelecimentos/`, payload)
      .then((r) => r.data),
};

export const usuariosApi = {
  me: () => api.get('/usuarios/me').then((r) => r.data),
  updateMe: (payload: { nome_completo?: string; telefone?: string; foto_path?: string }) =>
    api.patch('/usuarios/me', payload).then((r) => r.data),
  pedirExclusao: () => api.post('/usuarios/me/excluir').then((r) => r.data),
};
