import { api } from '@/api/client';
import type {
  Avaliacao,
  ID,
  Mensagem,
  MotivoCancelamento,
  Negociacao,
  Oportunidade,
  PapelTipo,
  Proposta,
  PublicacaoTipo,
  ReputacaoConta,
} from '@/types/api';

export const negociacoesApi = {
  list: () => api.get<Negociacao[]>('/negociacoes/').then((r) => r.data),
  get: (id: ID) => api.get<Negociacao>(`/negociacoes/${id}`).then((r) => r.data),
  abrir: (payload: { publicacao_id: ID; publicacao_tipo: PublicacaoTipo }) =>
    api.post<Negociacao>('/negociacoes/', payload).then((r) => r.data),
  sinalizarCombinado: (id: ID) =>
    api.post<Negociacao>(`/negociacoes/${id}/sinalizar-combinado`).then((r) => r.data),
  confirmarCombinado: (id: ID) =>
    api.post<Negociacao>(`/negociacoes/${id}/confirmar-combinado`).then((r) => r.data),
  aceitarLocalizacao: (id: ID) =>
    api.post<Negociacao>(`/negociacoes/${id}/aceitar-localizacao`).then((r) => r.data),
  localizacaoExata: (id: ID) =>
    api
      .get<{ lat: number; lng: number }>(`/negociacoes/${id}/localizacao-exata`)
      .then((r) => r.data),
  concluir: (id: ID) => api.post<Negociacao>(`/negociacoes/${id}/concluir`).then((r) => r.data),
  cancelar: (id: ID, motivo: MotivoCancelamento, texto: string) =>
    api.post<Negociacao>(`/negociacoes/${id}/cancelar`, { motivo, texto }).then((r) => r.data),
  disputar: (id: ID) => api.post<Negociacao>(`/negociacoes/${id}/disputar`).then((r) => r.data),
};

export const mensagensApi = {
  list: (negociacaoId: ID) =>
    api.get<Mensagem[]>(`/negociacoes/${negociacaoId}/mensagens/`).then((r) => r.data),
  enviar: (negociacaoId: ID, conteudo: string) =>
    api
      .post<Mensagem>(`/negociacoes/${negociacaoId}/mensagens/`, { conteudo })
      .then((r) => r.data),
};

export const avaliacoesApi = {
  avaliar: (
    negociacaoId: ID,
    payload: { nota: number; papel_avaliado: PapelTipo; subnotas?: Record<string, unknown>; comentario?: string },
  ) =>
    api
      .post<Avaliacao>(`/negociacoes/${negociacaoId}/avaliacoes`, payload)
      .then((r) => r.data),
  reputacaoDaConta: (contaId: ID) =>
    api.get<ReputacaoConta>(`/contas/${contaId}/reputacao`).then((r) => r.data),
};

export const oportunidadesApi = {
  list: () => api.get<Oportunidade[]>('/oportunidades/').then((r) => r.data),
  get: (id: ID) => api.get<Oportunidade>(`/oportunidades/${id}`).then((r) => r.data),
  criar: (payload: {
    titulo: string;
    descricao: string;
    subcategoria_id: ID;
    tipo: 'licitacao' | 'concorrencia' | 'chamada_publica' | 'chamada_privada';
    documentos_exigidos: string[];
    prazo_submissao: string;
    valor_estimado?: number | string;
  }) => api.post<Oportunidade>('/oportunidades/', payload).then((r) => r.data),
  submeterProposta: (
    opId: ID,
    payload: { valor: number | string; condicoes?: string; documentos_anexos: string[] },
  ) => api.post<Proposta>(`/oportunidades/${opId}/propostas`, payload).then((r) => r.data),
  listarPropostas: (opId: ID) =>
    api.get<Proposta[]>(`/oportunidades/${opId}/propostas`).then((r) => r.data),
  declararVencedor: (opId: ID, propostaId: ID) =>
    api
      .post<Oportunidade>(`/oportunidades/${opId}/declarar-vencedor`, null, {
        params: { proposta_id: propostaId },
      })
      .then((r) => r.data),
  encerrar: (opId: ID) =>
    api.post<Oportunidade>(`/oportunidades/${opId}/encerrar`).then((r) => r.data),
};
