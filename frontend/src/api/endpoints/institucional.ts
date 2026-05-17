import { api } from '@/api/client';
import type {
  Campanha,
  CampanhaStatus,
  ID,
  PedidoColeta,
  PedidoColetaStatus,
} from '@/types/api';

export const pedidosColetaApi = {
  list: () => api.get<PedidoColeta[]>('/pedidos-coleta/').then((r) => r.data),
  criar: (payload: {
    bairro: string;
    cidade: string;
    uf: string;
    ibge_municipio?: string;
    tipo_residuo: string;
    foto_path?: string;
    quantidade_estimada?: number | string;
    descricao?: string;
    localizacao: { lat: number; lng: number };
  }) => api.post<PedidoColeta>('/pedidos-coleta/', payload).then((r) => r.data),
  atualizarStatus: (id: ID, status: PedidoColetaStatus, nota?: string) =>
    api
      .patch<PedidoColeta>(`/pedidos-coleta/${id}/status`, { status, nota })
      .then((r) => r.data),
  contestar: (id: ID) =>
    api.post<PedidoColeta>(`/pedidos-coleta/${id}/contestar`).then((r) => r.data),
};

export const campanhasApi = {
  list: (ibge?: string) =>
    api.get<Campanha[]>('/campanhas/', { params: { ibge } }).then((r) => r.data),
  criar: (payload: {
    titulo: string;
    descricao: string;
    data_evento?: string;
    tipo_residuo?: string;
    beneficio?: string;
    cidade?: string;
    uf?: string;
    ibge_municipio?: string;
  }) => api.post<Campanha>('/campanhas/', payload).then((r) => r.data),
  atualizar: (id: ID, payload: Partial<Campanha> & { status?: CampanhaStatus }) =>
    api.patch<Campanha>(`/campanhas/${id}`, payload).then((r) => r.data),
};

export const mapaInstitucionalApi = {
  consultar: (ibge: string) =>
    api
      .get<{
        territorio: string;
        celulas: Array<{
          bairro: string;
          ibge_municipio: string | null;
          anuncios_ativos: number;
          pedidos_abertos: number;
          campanhas_ativas: number;
        }>;
      }>('/mapa-institucional/', { params: { ibge } })
      .then((r) => r.data),
};
