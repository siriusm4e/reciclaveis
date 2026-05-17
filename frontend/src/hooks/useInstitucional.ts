import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  campanhasApi,
  mapaInstitucionalApi,
  pedidosColetaApi,
} from '@/api/endpoints/institucional';
import type { ID, PedidoColetaStatus } from '@/types/api';

export function usePedidosColeta() {
  return useQuery({ queryKey: ['pedidos-coleta'], queryFn: pedidosColetaApi.list });
}

export function useCriarPedidoColeta() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: pedidosColetaApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pedidos-coleta'] }),
  });
}

export function useAtualizarStatusPedido() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { id: ID; status: PedidoColetaStatus; nota?: string }) =>
      pedidosColetaApi.atualizarStatus(p.id, p.status, p.nota),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pedidos-coleta'] }),
  });
}

export function useContestarPedido() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: ID) => pedidosColetaApi.contestar(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pedidos-coleta'] }),
  });
}

export function useCampanhas(ibge?: string) {
  return useQuery({
    queryKey: ['campanhas', ibge],
    queryFn: () => campanhasApi.list(ibge),
  });
}

export function useCriarCampanha() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: campanhasApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campanhas'] }),
  });
}

export function useMapaInstitucional(ibge: string | null) {
  return useQuery({
    queryKey: ['mapa-institucional', ibge],
    queryFn: () => mapaInstitucionalApi.consultar(ibge as string),
    enabled: Boolean(ibge),
  });
}
