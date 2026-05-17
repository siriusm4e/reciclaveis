import { api } from '@/api/client';
import type {
  Assinatura,
  Fatura,
  ID,
  PacoteCredito,
  PagamentoMetodo,
  PapelTipo,
  Plano,
  SaldoCreditos,
  TransacaoCredito,
} from '@/types/api';

export const creditosApi = {
  saldo: () => api.get<SaldoCreditos>('/creditos/saldo').then((r) => r.data),
  transacoes: (page = 1, page_size = 50) =>
    api
      .get<TransacaoCredito[]>('/creditos/transacoes', { params: { page, page_size } })
      .then((r) => r.data),
  pacotes: () => api.get<PacoteCredito[]>('/creditos/pacotes').then((r) => r.data),
  comprar: (pacote_id: ID, metodo: PagamentoMetodo) =>
    api.post<TransacaoCredito>('/creditos/comprar', { pacote_id, metodo }).then((r) => r.data),
};

export const planosApi = {
  porPapel: (papel: PapelTipo) =>
    api.get<Plano[]>('/planos/', { params: { papel } }).then((r) => r.data),
};

export const assinaturasApi = {
  list: () => api.get<Assinatura[]>('/assinaturas/').then((r) => r.data),
  assinar: (papel_id: ID, plano_id: ID) =>
    api.post<Assinatura>('/assinaturas/', { papel_id, plano_id }).then((r) => r.data),
  cancelar: (id: ID) =>
    api.post<Assinatura>(`/assinaturas/${id}/cancelar`).then((r) => r.data),
};

export const faturasApi = {
  list: () => api.get<Fatura[]>('/faturas/').then((r) => r.data),
  pagar: (id: ID, metodo: PagamentoMetodo = 'cartao') =>
    api.post(`/faturas/${id}/pagar`, null, { params: { metodo } }).then((r) => r.data),
};
