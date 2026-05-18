import { api } from '@/api/client';
import type { Categoria, ID, Subcategoria, TipoMaterial } from '@/types/api';

export const catalogoApi = {
  listarCategorias: () => api.get<Categoria[]>('/categorias/').then((r) => r.data),
  listarSubcategorias: (categoriaId: ID) =>
    api.get<Subcategoria[]>(`/categorias/${categoriaId}/subcategorias`).then((r) => r.data),
  listarTiposMaterial: (subcategoriaId: ID) =>
    api.get<TipoMaterial[]>(`/subcategorias/${subcategoriaId}/tipos`).then((r) => r.data),
  getTipoMaterial: (tipoId: ID) =>
    api.get<TipoMaterial>(`/tipos/${tipoId}`).then((r) => r.data),
  getAtributos: (tipoId: ID) =>
    api
      .get<{
        comuns: Array<{
          chave: string;
          label: string;
          tipo: string;
          enum_valores?: string[] | null;
        }>;
        especificos: Record<string, unknown>;
        unidade_padrao: string;
        requer_validacao_documental: boolean;
        documentos_exigidos: string[];
      }>(`/tipos/${tipoId}/atributos`)
      .then((r) => r.data),
};
