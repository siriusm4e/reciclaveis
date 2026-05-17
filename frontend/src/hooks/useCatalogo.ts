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

export function useAtributos(subcategoriaId: ID | null) {
  return useQuery({
    queryKey: ['subcategorias', subcategoriaId, 'atributos'],
    queryFn: () => catalogoApi.getAtributos(subcategoriaId as ID),
    enabled: Boolean(subcategoriaId),
    staleTime: 5 * 60_000,
  });
}
