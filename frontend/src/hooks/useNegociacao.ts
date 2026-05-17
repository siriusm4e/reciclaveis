import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  avaliacoesApi,
  mensagensApi,
  negociacoesApi,
  oportunidadesApi,
} from '@/api/endpoints/negociacao';
import type { ID, MotivoCancelamento, PapelTipo, PublicacaoTipo } from '@/types/api';

export function useNegociacoes() {
  return useQuery({ queryKey: ['negociacoes'], queryFn: negociacoesApi.list });
}

export function useNegociacao(id: ID | null) {
  return useQuery({
    queryKey: ['negociacoes', id],
    queryFn: () => negociacoesApi.get(id as ID),
    enabled: Boolean(id),
  });
}

export function useAbrirNegociacao() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { publicacao_id: ID; publicacao_tipo: PublicacaoTipo }) =>
      negociacoesApi.abrir(p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['negociacoes'] }),
  });
}

export function useAcoesNegociacao(negociacaoId: ID) {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ['negociacoes'] });

  return {
    sinalizar: useMutation({
      mutationFn: () => negociacoesApi.sinalizarCombinado(negociacaoId),
      onSuccess: invalidate,
    }),
    confirmar: useMutation({
      mutationFn: () => negociacoesApi.confirmarCombinado(negociacaoId),
      onSuccess: invalidate,
    }),
    aceitarLocalizacao: useMutation({
      mutationFn: () => negociacoesApi.aceitarLocalizacao(negociacaoId),
      onSuccess: invalidate,
    }),
    concluir: useMutation({
      mutationFn: () => negociacoesApi.concluir(negociacaoId),
      onSuccess: invalidate,
    }),
    cancelar: useMutation({
      mutationFn: (p: { motivo: MotivoCancelamento; texto: string }) =>
        negociacoesApi.cancelar(negociacaoId, p.motivo, p.texto),
      onSuccess: invalidate,
    }),
    disputar: useMutation({
      mutationFn: () => negociacoesApi.disputar(negociacaoId),
      onSuccess: invalidate,
    }),
  };
}

export function useLocalizacaoExata(negociacaoId: ID, enabled: boolean) {
  return useQuery({
    queryKey: ['negociacoes', negociacaoId, 'localizacao-exata'],
    queryFn: () => negociacoesApi.localizacaoExata(negociacaoId),
    enabled,
    staleTime: Infinity,
  });
}

// ===== Mensagens =====

export function useMensagens(negociacaoId: ID | null) {
  return useQuery({
    queryKey: ['mensagens', negociacaoId],
    queryFn: () => mensagensApi.list(negociacaoId as ID),
    enabled: Boolean(negociacaoId),
  });
}

export function useEnviarMensagem(negociacaoId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (conteudo: string) => mensagensApi.enviar(negociacaoId, conteudo),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['mensagens', negociacaoId] }),
  });
}

// ===== Avaliações =====

export function useAvaliar(negociacaoId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { nota: number; papel_avaliado: PapelTipo; comentario?: string }) =>
      avaliacoesApi.avaliar(negociacaoId, { ...p, subnotas: {} }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['negociacoes', negociacaoId] }),
  });
}

export function useReputacao(contaId: ID | null) {
  return useQuery({
    queryKey: ['reputacao', contaId],
    queryFn: () => avaliacoesApi.reputacaoDaConta(contaId as ID),
    enabled: Boolean(contaId),
  });
}

// ===== Oportunidades =====

export function useOportunidades() {
  return useQuery({ queryKey: ['oportunidades'], queryFn: oportunidadesApi.list });
}

export function useOportunidade(id: ID | null) {
  return useQuery({
    queryKey: ['oportunidades', id],
    queryFn: () => oportunidadesApi.get(id as ID),
    enabled: Boolean(id),
  });
}

export function useCriarOportunidade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: oportunidadesApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['oportunidades'] }),
  });
}

export function useSubmeterProposta(opId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: Parameters<typeof oportunidadesApi.submeterProposta>[1]) =>
      oportunidadesApi.submeterProposta(opId, p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['oportunidades', opId] }),
  });
}
