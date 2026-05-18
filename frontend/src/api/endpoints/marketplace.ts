import { api } from '@/api/client';
import type {
  AlertaPagoConfig,
  AlertaPagoResultado,
  AnuncioFrete,
  AnuncioMaquina,
  AnuncioServico,
  AnuncioVenda,
  CondicaoEquipamento,
  CondicaoForma,
  CondicaoLimpeza,
  CondicaoUmidade,
  FrequenciaAnuncio,
  ID,
  ModalidadeMaquina,
  OfertaCompra,
  UnidadeCobrancaServico,
} from '@/types/api';

export interface BuscaAnuncioParams {
  categoria_id?: ID;
  subcategoria_id?: ID;
  tipo_material_id?: ID;
  lat?: number;
  lng?: number;
  raio_km?: number;
  preco_min?: number;
  preco_max?: number;
  // Filtro mútuo de visibilidade por volume
  volume_minimo_kg?: number; // usado em buscar anúncios (comprador exige X kg)
  volume_disponivel_kg?: number; // usado em buscar ofertas (vendedor tem X kg)
  // Condição (grupos exclusivos)
  condicao_limpeza?: CondicaoLimpeza;
  condicao_umidade?: CondicaoUmidade;
  condicao_forma?: CondicaoForma;
  page?: number;
  page_size?: number;
}

export const anunciosVendaApi = {
  buscar: (params: BuscaAnuncioParams = {}) =>
    api.get<AnuncioVenda[]>('/anuncios-venda/', { params }).then((r) => r.data),
  get: (id: ID) => api.get<AnuncioVenda>(`/anuncios-venda/${id}`).then((r) => r.data),
  criar: (payload: {
    papel_id: ID;
    tipo_material_id: ID;
    atributos: Record<string, unknown>;
    condicao_limpeza?: CondicaoLimpeza;
    condicao_umidade?: CondicaoUmidade;
    condicao_forma?: CondicaoForma;
    localizacao_real: { lat: number; lng: number };
    territorio: 'urbano' | 'rural';
    preco_pretendido: number | string;
    unidade: string;
    volume_estimado?: number | string;
    frequencia: FrequenciaAnuncio;
    intervalo_geracao?: string;
    prazo_validade: string;
    fotos: string[]; // máximo 3
    aceita_alerta_pago_de_terceiros?: boolean;
  }) => api.post<AnuncioVenda>('/anuncios-venda/', payload).then((r) => r.data),
  atualizar: (id: ID, payload: Partial<AnuncioVenda>) =>
    api.patch<AnuncioVenda>(`/anuncios-venda/${id}`, payload).then((r) => r.data),
  replicar: (id: ID) =>
    api.post<AnuncioVenda>(`/anuncios-venda/${id}/replicar`).then((r) => r.data),
  precoReferencia: (id: ID, cidade?: string) =>
    api
      .get<{ subcategoria_id: ID; cidade: string | null; amostra: number; preco_medio: string | null }>(
        `/anuncios-venda/${id}/preco-referencia`,
        { params: { cidade } },
      )
      .then((r) => r.data),
};

export const ofertasCompraApi = {
  buscar: (params: BuscaAnuncioParams = {}) =>
    api.get<OfertaCompra[]>('/ofertas-compra/', { params }).then((r) => r.data),
  get: (id: ID) => api.get<OfertaCompra>(`/ofertas-compra/${id}`).then((r) => r.data),
  criar: (payload: {
    papel_id: ID;
    tipo_material_id: ID;
    titulo: string;
    descricao?: string;
    especificacao: Record<string, unknown>;
    preco_paga: number | string;
    unidade: string;
    volume_min: number | string;
    volume_max?: number | string;
    volume_minimo_kg?: number; // filtro mútuo de visibilidade
    condicao_limpeza?: CondicaoLimpeza;
    condicao_umidade?: CondicaoUmidade;
    condicao_forma?: CondicaoForma;
    localizacao: { lat: number; lng: number };
    raio_km: number;
    retira: boolean;
    prazo_validade: string;
  }) => api.post<OfertaCompra>('/ofertas-compra/', payload).then((r) => r.data),
  atualizar: (id: ID, payload: Partial<OfertaCompra>) =>
    api.patch<OfertaCompra>(`/ofertas-compra/${id}`, payload).then((r) => r.data),
  ativarAlertaPago: (id: ID, payload: AlertaPagoConfig) =>
    api
      .post<AlertaPagoResultado>(`/ofertas-compra/${id}/ativar-alerta-pago`, payload)
      .then((r) => r.data),
};

export const maquinasApi = {
  buscar: (params: { categoria_equipamento?: string; lat?: number; lng?: number; raio_km?: number } = {}) =>
    api.get<AnuncioMaquina[]>('/anuncios-maquina/', { params }).then((r) => r.data),
  get: (id: ID) => api.get<AnuncioMaquina>(`/anuncios-maquina/${id}`).then((r) => r.data),
  criar: (payload: {
    papel_id?: ID;
    categoria_equipamento: string;
    marca?: string;
    modelo?: string;
    ano?: number;
    capacidade?: string;
    tensao?: string;
    descricao?: string;
    condicao: CondicaoEquipamento;
    modalidade: ModalidadeMaquina;
    aceita_visita_tecnica?: boolean;
    disponibilidade?: Record<string, unknown>;
    preco: number | string;
    documentacao_disponivel?: boolean;
    fotos: string[];
    localizacao: { lat: number; lng: number };
    prazo_validade: string;
  }) => api.post<AnuncioMaquina>('/anuncios-maquina/', payload).then((r) => r.data),
  manutencaoProxima: (id: ID) =>
    api.get(`/anuncios-maquina/${id}/manutencao-proxima`).then((r) => r.data),
};

export const servicosApi = {
  buscar: (params: { tipo_servico?: string; lat?: number; lng?: number; raio_km?: number } = {}) =>
    api.get<AnuncioServico[]>('/anuncios-servico/', { params }).then((r) => r.data),
  get: (id: ID) => api.get<AnuncioServico>(`/anuncios-servico/${id}`).then((r) => r.data),
  criar: (payload: {
    papel_id: ID;
    tipo_servico: string;
    descricao?: string;
    raio_operacional_km: number;
    unidade_cobranca: UnidadeCobrancaServico;
    preco?: number | string;
    requer_visita_tecnica?: boolean;
    disponibilidade?: Record<string, unknown>;
    localizacao: { lat: number; lng: number };
    prazo_validade: string;
  }) => api.post<AnuncioServico>('/anuncios-servico/', payload).then((r) => r.data),
};

export const fretesApi = {
  buscar: (params: {
    tipo_veiculo?: string;
    categoria_aceita?: string;
    lat?: number;
    lng?: number;
    raio_km?: number;
  } = {}) => api.get<AnuncioFrete[]>('/anuncios-frete/', { params }).then((r) => r.data),
  get: (id: ID) => api.get<AnuncioFrete>(`/anuncios-frete/${id}`).then((r) => r.data),
  criar: (payload: {
    papel_id: ID;
    tipo_veiculo: string;
    capacidade_t?: number | string;
    capacidade_m3?: number | string;
    tara?: number | string;
    raio_operacional_km: number;
    categorias_residuo_aceitas: string[];
    licencas: string[];
    emite_nf?: boolean;
    localizacao: { lat: number; lng: number };
    prazo_validade: string;
  }) => api.post<AnuncioFrete>('/anuncios-frete/', payload).then((r) => r.data),
};
