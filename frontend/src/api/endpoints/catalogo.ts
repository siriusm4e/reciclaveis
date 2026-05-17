import { api } from '@/api/client';
import type { Categoria, ID, Subcategoria } from '@/types/api';

export const catalogoApi = {
  listarCategorias: () => api.get<Categoria[]>('/categorias/').then((r) => r.data),
  listarSubcategorias: (categoriaId: ID) =>
    api.get<Subcategoria[]>(`/categorias/${categoriaId}/subcategorias`).then((r) => r.data),
  getAtributos: (subcategoriaId: ID) =>
    api
      .get<{
        comuns: Array<{
          chave: string;
          label: string;
          tipo: string;
          enum_valores?: string[] | null;
        }>;
        especificos: Record<string, unknown>;
        requer_validacao_documental: boolean;
        documentos_exigidos: string[];
      }>(`/subcategorias/${subcategoriaId}/atributos`)
      .then((r) => r.data),
};
