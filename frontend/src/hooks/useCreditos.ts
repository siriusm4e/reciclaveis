import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  assinaturasApi,
  creditosApi,
  faturasApi,
  planosApi,
} from '@/api/endpoints/creditos';
import type { ID, PagamentoMetodo, PapelTipo } from '@/types/api';

export function useSaldoCreditos() {
  return useQuery({ queryKey: ['creditos', 'saldo'], queryFn: creditosApi.saldo, staleTime: 30_000 });
}

export function useTransacoesCredito(page = 1) {
  return useQuery({
    queryKey: ['creditos', 'transacoes', page],
    queryFn: () => creditosApi.transacoes(page),
  });
}

export function usePacotesCredito() {
  return useQuery({ queryKey: ['creditos', 'pacotes'], queryFn: creditosApi.pacotes });
}

export function useComprarPacote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { pacote_id: ID; metodo: PagamentoMetodo }) =>
      creditosApi.comprar(p.pacote_id, p.metodo),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['creditos'] }),
  });
}

export function usePlanosPorPapel(papel: PapelTipo | null) {
  return useQuery({
    queryKey: ['planos', papel],
    queryFn: () => planosApi.porPapel(papel as PapelTipo),
    enabled: Boolean(papel),
  });
}

export function useMinhasAssinaturas() {
  return useQuery({ queryKey: ['assinaturas'], queryFn: assinaturasApi.list });
}

export function useAssinar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { papel_id: ID; plano_id: ID }) => assinaturasApi.assinar(p.papel_id, p.plano_id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['assinaturas'] }),
  });
}

export function useCancelarAssinatura() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: ID) => assinaturasApi.cancelar(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['assinaturas'] }),
  });
}

export function useFaturas() {
  return useQuery({ queryKey: ['faturas'], queryFn: faturasApi.list });
}

export function usePagarFatura() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { id: ID; metodo?: PagamentoMetodo }) => faturasApi.pagar(p.id, p.metodo),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['faturas'] }),
  });
}
