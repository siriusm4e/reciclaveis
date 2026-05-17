import { api } from '@/api/client';
import type {
  AcaoModeracao,
  Denuncia,
  DenunciaAlvoTipo,
  DenunciaTipoFechado,
  ID,
} from '@/types/api';

export const denunciasApi = {
  list: () => api.get<Denuncia[]>('/denuncias/').then((r) => r.data),
  abrir: (payload: {
    alvo_tipo: DenunciaAlvoTipo;
    alvo_id: ID;
    tipo_fechado: DenunciaTipoFechado;
    descricao: string;
  }) => api.post<Denuncia>('/denuncias/', payload).then((r) => r.data),
};

// Backoffice
export const adminApi = {
  contas: {
    list: (params: { tipo?: string; status?: string; page?: number; page_size?: number } = {}) =>
      api.get('/admin/contas/', { params }).then((r) => r.data),
    mudarStatus: (id: ID, status: string, motivo: string) =>
      api.patch(`/admin/contas/${id}/status`, { status, motivo }).then((r) => r.data),
    cortesia: (id: ID) => api.post(`/admin/contas/${id}/cortesia`).then((r) => r.data),
  },
  documentos: {
    fila: () => api.get('/admin/documentos/fila').then((r) => r.data),
    aprovar: (id: ID) => api.post(`/admin/documentos/${id}/aprovar`).then((r) => r.data),
    rejeitar: (id: ID, motivo: string) =>
      api.post(`/admin/documentos/${id}/rejeitar`, { motivo }).then((r) => r.data),
  },
  catalogo: {
    criarCategoria: (p: Record<string, unknown>) =>
      api.post('/admin/categorias/', p).then((r) => r.data),
    atualizarCategoria: (id: ID, p: Record<string, unknown>) =>
      api.patch(`/admin/categorias/${id}`, p).then((r) => r.data),
    criarSubcategoria: (p: Record<string, unknown>) =>
      api.post('/admin/subcategorias/', p).then((r) => r.data),
    atualizarSubcategoria: (id: ID, p: Record<string, unknown>) =>
      api.patch(`/admin/subcategorias/${id}`, p).then((r) => r.data),
    criarTipoDoc: (p: Record<string, unknown>) =>
      api.post('/admin/tipos-documento/', p).then((r) => r.data),
    atualizarTipoDoc: (id: ID, p: Record<string, unknown>) =>
      api.patch(`/admin/tipos-documento/${id}`, p).then((r) => r.data),
  },
  creditos: {
    listarPacotes: () => api.get('/admin/pacotes-credito/').then((r) => r.data),
    criarPacote: (p: Record<string, unknown>) =>
      api.post('/admin/pacotes-credito/', p).then((r) => r.data),
    ajuste: (conta_id: ID, valor: number, descricao: string) =>
      api
        .post('/admin/creditos/ajuste', null, { params: { conta_id, valor, descricao } })
        .then((r) => r.data),
  },
  assinaturas: {
    planos: () => api.get('/admin/planos/').then((r) => r.data),
    criarPlano: (p: Record<string, unknown>) => api.post('/admin/planos/', p).then((r) => r.data),
    cortesia: (id: ID) => api.post(`/admin/assinaturas/${id}/cortesia`).then((r) => r.data),
  },
  moderacao: {
    fila: (page = 1, page_size = 50) =>
      api.get('/admin/denuncias/', { params: { page, page_size } }).then((r) => r.data),
    decidir: (id: ID, acao: AcaoModeracao, motivo: string) =>
      api.post(`/admin/denuncias/${id}/decidir`, { acao, motivo }).then((r) => r.data),
  },
  conteudo: {
    criar: (p: Record<string, unknown>) => api.post('/admin/conteudo/', p).then((r) => r.data),
    atualizar: (id: ID, p: Record<string, unknown>) =>
      api.patch(`/admin/conteudo/${id}`, p).then((r) => r.data),
    dispararComunicacao: (p: {
      titulo: string;
      corpo: string;
      finalidade: string;
      segmentacao?: Record<string, unknown>;
    }) => api.post('/admin/comunicacao/disparar', p).then((r) => r.data),
  },
  analytics: {
    publicacoes: () => api.get('/admin/analytics/publicacoes').then((r) => r.data),
    liquidez: () => api.get('/admin/analytics/liquidez').then((r) => r.data),
    precoMedio: (subcategoria_id: ID, cidade?: string) =>
      api
        .get('/admin/analytics/preco-medio', { params: { subcategoria_id, cidade } })
        .then((r) => r.data),
  },
  perfis: {
    list: () => api.get('/admin/perfis-internos/').then((r) => r.data),
    criar: (usuario_id: ID, tipo: string) =>
      api.post('/admin/perfis-internos/', { usuario_id, tipo }).then((r) => r.data),
    auditLog: (params: { recurso_tipo?: string; recurso_id?: ID; page?: number; page_size?: number } = {}) =>
      api.get('/admin/audit-log/', { params }).then((r) => r.data),
    setLimiarCobertura: (valor: number) =>
      api.patch('/admin/config/limiar-cobertura', { valor }).then((r) => r.data),
    setPrazoOportunidade: (dias_uteis: number) =>
      api.patch('/admin/config/prazo-oportunidade-publica', { dias_uteis }).then((r) => r.data),
  },
};
