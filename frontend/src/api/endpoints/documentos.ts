import { api } from '@/api/client';
import type { Documento, ID, TipoDocumento } from '@/types/api';

export const tiposDocApi = {
  list: (papel?: string) =>
    api
      .get<TipoDocumento[]>('/tipos-documento/', { params: papel ? { papel } : undefined })
      .then((r) => r.data),
};

export const documentosApi = {
  list: () => api.get<Documento[]>('/documentos/').then((r) => r.data),
  get: (id: ID) => api.get<Documento>(`/documentos/${id}`).then((r) => r.data),
  upload: async (
    file: File,
    payload: {
      tipo_documento_id: ID;
      estabelecimento_id?: ID;
      numero?: string;
      data_emissao?: string;
      data_vencimento?: string;
    },
  ) => {
    const form = new FormData();
    form.append('arquivo', file);
    form.append('tipo_documento_id', payload.tipo_documento_id);
    if (payload.estabelecimento_id) form.append('estabelecimento_id', payload.estabelecimento_id);
    if (payload.numero) form.append('numero', payload.numero);
    if (payload.data_emissao) form.append('data_emissao', payload.data_emissao);
    if (payload.data_vencimento) form.append('data_vencimento', payload.data_vencimento);
    const { data } = await api.post<Documento>('/documentos/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
  renovar: async (
    docId: ID,
    file: File,
    payload: { numero?: string; data_emissao?: string; data_vencimento?: string } = {},
  ) => {
    const form = new FormData();
    form.append('arquivo', file);
    if (payload.numero) form.append('numero', payload.numero);
    if (payload.data_emissao) form.append('data_emissao', payload.data_emissao);
    if (payload.data_vencimento) form.append('data_vencimento', payload.data_vencimento);
    const { data } = await api.post<Documento>(`/documentos/${docId}/renovar`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};
