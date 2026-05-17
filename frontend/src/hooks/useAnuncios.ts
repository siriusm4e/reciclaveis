import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  anunciosVendaApi,
  fretesApi,
  maquinasApi,
  ofertasCompraApi,
  servicosApi,
  type BuscaAnuncioParams,
} from '@/api/endpoints/marketplace';
import type { ID } from '@/types/api';

// ===== AnuncioVenda =====

export function useBuscarAnuncios(params: BuscaAnuncioParams) {
  return useQuery({
    queryKey: ['anuncios-venda', params],
    queryFn: () => anunciosVendaApi.buscar(params),
    staleTime: 30_000,
  });
}

export function useAnuncio(id: ID | null) {
  return useQuery({
    queryKey: ['anuncios-venda', id],
    queryFn: () => anunciosVendaApi.get(id as ID),
    enabled: Boolean(id),
  });
}

export function useCriarAnuncio() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: anunciosVendaApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['anuncios-venda'] }),
  });
}

export function useAtualizarAnuncio(id: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Parameters<typeof anunciosVendaApi.atualizar>[1]) =>
      anunciosVendaApi.atualizar(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['anuncios-venda'] }),
  });
}

// ===== OfertaCompra =====

export function useBuscarOfertas(params: BuscaAnuncioParams) {
  return useQuery({
    queryKey: ['ofertas-compra', params],
    queryFn: () => ofertasCompraApi.buscar(params),
    staleTime: 30_000,
  });
}

export function useOferta(id: ID | null) {
  return useQuery({
    queryKey: ['ofertas-compra', id],
    queryFn: () => ofertasCompraApi.get(id as ID),
    enabled: Boolean(id),
  });
}

export function useCriarOferta() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ofertasCompraApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ofertas-compra'] }),
  });
}

export function useAtivarAlertaPago(ofertaId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (cfg: Parameters<typeof ofertasCompraApi.ativarAlertaPago>[1]) =>
      ofertasCompraApi.ativarAlertaPago(ofertaId, cfg),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ofertas-compra'] }),
  });
}

// ===== Máquinas / Serviços / Fretes =====

export function useBuscarMaquinas(params: Parameters<typeof maquinasApi.buscar>[0]) {
  return useQuery({
    queryKey: ['anuncios-maquina', params],
    queryFn: () => maquinasApi.buscar(params),
  });
}
export function useMaquina(id: ID | null) {
  return useQuery({
    queryKey: ['anuncios-maquina', id],
    queryFn: () => maquinasApi.get(id as ID),
    enabled: Boolean(id),
  });
}
export function useManutencaoProxima(id: ID | null) {
  return useQuery({
    queryKey: ['anuncios-maquina', id, 'manutencao-proxima'],
    queryFn: () => maquinasApi.manutencaoProxima(id as ID),
    enabled: Boolean(id),
  });
}
export function useCriarMaquina() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: maquinasApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['anuncios-maquina'] }),
  });
}

export function useBuscarServicos(params: Parameters<typeof servicosApi.buscar>[0]) {
  return useQuery({ queryKey: ['anuncios-servico', params], queryFn: () => servicosApi.buscar(params) });
}
export function useCriarServico() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: servicosApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['anuncios-servico'] }),
  });
}

export function useBuscarFretes(params: Parameters<typeof fretesApi.buscar>[0]) {
  return useQuery({ queryKey: ['anuncios-frete', params], queryFn: () => fretesApi.buscar(params) });
}
export function useCriarFrete() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: fretesApi.criar,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['anuncios-frete'] }),
  });
}
