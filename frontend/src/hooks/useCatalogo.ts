import { useQuery } from '@tanstack/react-query';

import { catalogoApi } from '@/api/endpoints/catalogo';
import type { ID } from '@/types/api';

export function useCategorias() {
  return useQuery({
    queryKey: ['categorias'],
    queryFn: catalogoApi.listarCategorias,
    staleTime: 5 * 60_000,
  });
}

export function useSubcategorias(categoriaId: ID | null) {
  return useQuery({
    queryKey: ['categorias', categoriaId, 'subcategorias'],
    queryFn: () => catalogoApi.listarSubcategorias(categoriaId as ID),
    enabled: Boolean(categoriaId),
    staleTime: 5 * 60_000,
  });
}

export function useTiposMaterial(subcategoriaId: ID | null) {
  return useQuery({
    queryKey: ['subcategorias', subcategoriaId, 'tipos'],
    queryFn: () => catalogoApi.listarTiposMaterial(subcategoriaId as ID),
    enabled: Boolean(subcategoriaId),
    staleTime: 5 * 60_000,
  });
}

export function useTipoMaterial(tipoId: ID | null) {
  return useQuery({
    queryKey: ['tipos', tipoId],
    queryFn: () => catalogoApi.getTipoMaterial(tipoId as ID),
    enabled: Boolean(tipoId),
    staleTime: 5 * 60_000,
  });
}

export function useAtributos(tipoId: ID | null) {
  return useQuery({
    queryKey: ['tipos', tipoId, 'atributos'],
    queryFn: () => catalogoApi.getAtributos(tipoId as ID),
    enabled: Boolean(tipoId),
    staleTime: 5 * 60_000,
  });
}
