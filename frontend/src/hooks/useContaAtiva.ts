import { useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  contasApi,
  estabelecimentosApi,
  membrosApi,
  papeisApi,
} from '@/api/endpoints/identidade';
import { useAuthStore } from '@/store/authStore';
import { useContaStore } from '@/store/contaStore';
import type {
  Conta,
  ContaTipo,
  ID,
  PapelInternoMembro,
  PapelStatus,
  PapelTipo,
} from '@/types/api';

export function useMinhasContas() {
  const isAuth = useAuthStore((s) => Boolean(s.accessToken));
  return useQuery({
    queryKey: ['contas', 'minhas'],
    queryFn: contasApi.list,
    enabled: isAuth,
  });
}

/** Garante que houve uma Conta ativa selecionada (auto-seleciona se houver apenas uma). */
export function useAutoSelecionarConta() {
  const { data } = useMinhasContas();
  const contaAtiva = useContaStore((s) => s.contaAtiva);
  const setContaAtiva = useContaStore((s) => s.setContaAtiva);

  useEffect(() => {
    if (!data || data.length === 0) return;
    if (contaAtiva && data.some((c) => c.id === contaAtiva.id)) return;
    if (data.length === 1) {
      setContaAtiva(data[0]);
    }
  }, [data, contaAtiva, setContaAtiva]);
}

export function useContaAtiva() {
  return useContaStore((s) => s.contaAtiva);
}

export function useTrocarConta() {
  const setContaAtiva = useContaStore((s) => s.setContaAtiva);
  const qc = useQueryClient();
  return (c: Conta | null) => {
    setContaAtiva(c);
    qc.invalidateQueries();
  };
}

// ===== Criar / atualizar conta =====

export function useCriarConta() {
  const qc = useQueryClient();
  const setContaAtiva = useContaStore((s) => s.setContaAtiva);
  return useMutation({
    mutationFn: (p: {
      tipo: ContaTipo;
      nome_publico: string;
      cnpj?: string;
      escopo_territorial?: Record<string, unknown>;
    }) => contasApi.create(p),
    onSuccess: async (c) => {
      setContaAtiva(c);
      await qc.invalidateQueries({ queryKey: ['contas'] });
    },
  });
}

export function useAtualizarConta(contaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: Partial<Conta>) => contasApi.update(contaId, p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contas'] }),
  });
}

// ===== Membros / Papéis / Estabelecimentos =====

export function useMembros(contaId: ID | null) {
  return useQuery({
    queryKey: ['contas', contaId, 'membros'],
    queryFn: () => membrosApi.list(contaId as ID),
    enabled: Boolean(contaId),
  });
}

export function useConvidarMembro(contaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { email: string; papel_interno: PapelInternoMembro }) =>
      membrosApi.convidar(contaId, p.email, p.papel_interno),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contas', contaId, 'membros'] }),
  });
}

export function useRemoverMembro(contaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (membroId: ID) => membrosApi.remover(contaId, membroId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contas', contaId, 'membros'] }),
  });
}

export function usePapeis(contaId: ID | null) {
  return useQuery({
    queryKey: ['contas', contaId, 'papeis'],
    queryFn: () => papeisApi.list(contaId as ID),
    enabled: Boolean(contaId),
  });
}

export function useAtivarPapel(contaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { papel: PapelTipo; dados_complementares?: Record<string, unknown> }) =>
      papeisApi.ativar(contaId, p.papel, p.dados_complementares),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contas', contaId, 'papeis'] }),
  });
}

export function useAtualizarPapel(contaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { papelId: ID; dados_complementares?: Record<string, unknown>; status?: PapelStatus }) =>
      papeisApi.atualizar(contaId, p.papelId, { dados_complementares: p.dados_complementares, status: p.status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contas', contaId, 'papeis'] }),
  });
}

export function useEstabelecimentos(contaId: ID | null) {
  return useQuery({
    queryKey: ['contas', contaId, 'estabelecimentos'],
    queryFn: () => estabelecimentosApi.list(contaId as ID),
    enabled: Boolean(contaId),
  });
}

export function useCriarEstabelecimento(contaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (
      p: Parameters<typeof estabelecimentosApi.criar>[1],
    ) => estabelecimentosApi.criar(contaId, p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contas', contaId, 'estabelecimentos'] }),
  });
}
