import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { documentosApi, tiposDocApi } from '@/api/endpoints/documentos';
import type { ID } from '@/types/api';

export function useTiposDocumento(papel?: string) {
  return useQuery({
    queryKey: ['tipos-documento', papel ?? null],
    queryFn: () => tiposDocApi.list(papel),
    staleTime: 5 * 60_000,
  });
}

export function useDocumentos() {
  return useQuery({ queryKey: ['documentos'], queryFn: documentosApi.list });
}

export function useDocumento(id: ID | null) {
  return useQuery({
    queryKey: ['documentos', id],
    queryFn: () => documentosApi.get(id as ID),
    enabled: Boolean(id),
  });
}

export function useUploadDocumento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: {
      file: File;
      tipo_documento_id: ID;
      estabelecimento_id?: ID;
      numero?: string;
      data_emissao?: string;
      data_vencimento?: string;
    }) => documentosApi.upload(p.file, p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documentos'] }),
  });
}

export function useRenovarDocumento(docId: ID) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { file: File; numero?: string; data_emissao?: string; data_vencimento?: string }) =>
      documentosApi.renovar(docId, p.file, p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documentos'] }),
  });
}
