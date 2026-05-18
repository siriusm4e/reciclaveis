import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CenterSpinner } from '@/components/ui/states';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { showToast } from '@/components/ui/toaster';
import { useCategorias, useSubcategorias } from '@/hooks/useCatalogo';

export default function CatalogoAdmin() {
  const qc = useQueryClient();
  const { data: cats, isLoading } = useCategorias();
  const [catId, setCatId] = useState<string>('');
  const { data: subs } = useSubcategorias(catId || null);

  const criarCat = useMutation({
    mutationFn: (p: { nome: string; slug: string; cor_hex: string; icone: string }) =>
      adminApi.catalogo.criarCategoria({ ...p, ordem: 100, ativo: true }),
    onSuccess: () => {
      showToast({ title: 'Categoria criada', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['categorias'] });
    },
  });
  const criarSub = useMutation({
    mutationFn: (p: { categoria_id: string; nome: string; slug: string; unidade_padrao: string }) =>
      adminApi.catalogo.criarSubcategoria({
        ...p,
        requer_validacao_documental: false,
        documentos_exigidos: [],
        atributos_especificos: {},
        ordem: 100,
        ativo: true,
      }),
    onSuccess: () => {
      showToast({ title: 'Subcategoria criada', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['categorias'] });
    },
  });

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Catálogo</h1>
      <Tabs defaultValue="cats">
        <TabsList>
          <TabsTrigger value="cats">Categorias</TabsTrigger>
          <TabsTrigger value="subs">Subcategorias</TabsTrigger>
        </TabsList>

        <TabsContent value="cats">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              criarCat.mutate({
                nome: String(fd.get('nome')),
                slug: String(fd.get('slug')),
                cor_hex: String(fd.get('cor_hex')),
                icone: String(fd.get('icone')),
              });
              (e.target as HTMLFormElement).reset();
            }}
            className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4"
          >
            <div><Label>Nome</Label><Input name="nome" required /></div>
            <div><Label>Slug</Label><Input name="slug" required pattern="[a-z0-9-]+" /></div>
            <div><Label>Cor (#hex)</Label><Input name="cor_hex" required defaultValue="#1e8c4e" /></div>
            <div><Label>Ícone (lucide)</Label><Input name="icone" required defaultValue="recycle" /></div>
            <div className="md:col-span-4"><Button type="submit" loading={criarCat.isPending}>Criar categoria</Button></div>
          </form>

          {isLoading ? <CenterSpinner /> : (
            <div className="space-y-2">
              {cats?.map((c) => (
                <Card key={c.id} className="p-3 flex items-center justify-between">
                  <div>
                    <p className="font-bold">{c.nome}</p>
                    <p className="text-xs font-mono">{c.slug}</p>
                  </div>
                  <span className="font-mono text-xs">{c.cor_hex}</span>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="subs">
          <div className="mb-4">
            <Label>Selecione a categoria</Label>
            <select
              value={catId}
              onChange={(e) => setCatId(e.target.value)}
              className="w-full rounded-lg border border-neutral-200 p-2 bg-surface-input"
            >
              <option value="">—</option>
              {cats?.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>
          </div>

          {catId && (
            <>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const fd = new FormData(e.currentTarget);
                  criarSub.mutate({
                    categoria_id: catId,
                    nome: String(fd.get('nome')),
                    slug: String(fd.get('slug')),
                    unidade_padrao: String(fd.get('unidade')),
                  });
                  (e.target as HTMLFormElement).reset();
                }}
                className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4"
              >
                <div><Label>Nome</Label><Input name="nome" required /></div>
                <div><Label>Slug</Label><Input name="slug" required pattern="[a-z0-9-]+" /></div>
                <div><Label>Unidade</Label><Input name="unidade" required defaultValue="kg" /></div>
                <div className="md:col-span-3"><Button type="submit" loading={criarSub.isPending}>Criar subcategoria</Button></div>
              </form>

              <div className="space-y-2">
                {subs?.map((s) => (
                  <Card key={s.id} className="p-3">
                    <p className="font-bold">{s.nome}</p>
                    <p className="text-xs font-mono">{s.slug}</p>
                    {s.requer_validacao_documental && (
                      <p className="mt-1 text-xs text-warning-dark">Regulada — exige: {s.documentos_exigidos.join(', ')}</p>
                    )}
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
