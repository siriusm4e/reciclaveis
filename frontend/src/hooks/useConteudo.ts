import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { conteudoApi, preferenciasApi } from '@/api/endpoints/conteudo';
import type { ID, PreferenciaComunicacao } from '@/types/api';

export function useConteudos(params: { papel?: string; categoria?: string } = {}) {
  return useQuery({ queryKey: ['conteudo', params], queryFn: () => conteudoApi.list(params) });
}

export function useConteudo(id: ID | null) {
  return useQuery({
    queryKey: ['conteudo', id],
    queryFn: () => conteudoApi.get(id as ID),
    enabled: Boolean(id),
  });
}

export function usePreferencias() {
  return useQuery({ queryKey: ['preferencias'], queryFn: preferenciasApi.get });
}

export function useAtualizarPreferencias() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: Partial<PreferenciaComunicacao>) => preferenciasApi.update(p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['preferencias'] }),
  });
}
