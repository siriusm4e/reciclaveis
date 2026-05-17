import { useMutation } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { showToast } from '@/components/ui/toaster';

export default function ConteudoAdmin() {
  const criar = useMutation({
    mutationFn: adminApi.conteudo.criar,
    onSuccess: () => showToast({ title: 'Conteúdo criado', variant: 'success' }),
  });
  const disparar = useMutation({
    mutationFn: adminApi.conteudo.dispararComunicacao,
    onSuccess: (res) =>
      showToast({
        title: 'Disparo concluído',
        description: `Enviadas: ${(res as { enviados?: number })?.enviados ?? 0}`,
        variant: 'success',
      }),
  });

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold tracking-tighter mb-4">Novo conteúdo educativo</h1>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            criar.mutate({
              titulo: String(fd.get('titulo')),
              tipo: String(fd.get('tipo')),
              resumo: String(fd.get('resumo')),
              url: String(fd.get('url') || ''),
              conteudo: String(fd.get('conteudo') || ''),
              papeis_alvo: String(fd.get('papeis') || '').split(',').map((s) => s.trim()).filter(Boolean),
              categorias_alvo: String(fd.get('cats') || '').split(',').map((s) => s.trim()).filter(Boolean),
              publicado: true,
            });
            (e.target as HTMLFormElement).reset();
          }}
          className="grid grid-cols-1 md:grid-cols-2 gap-3"
        >
          <div><Label>Título</Label><Input name="titulo" required /></div>
          <div>
            <Label>Tipo</Label>
            <select name="tipo" className="w-full rounded-lg border border-neutral-200 p-2 bg-surface-input" defaultValue="artigo">
              <option value="artigo">Artigo</option>
              <option value="dica">Dica</option>
              <option value="curso">Curso</option>
              <option value="video">Vídeo</option>
            </select>
          </div>
          <div className="md:col-span-2"><Label>Resumo</Label><Textarea name="resumo" /></div>
          <div><Label>URL (opcional)</Label><Input name="url" /></div>
          <div><Label>Papéis alvo (slugs separados por vírgula)</Label><Input name="papeis" className="font-mono" /></div>
          <div><Label>Categorias alvo</Label><Input name="cats" className="font-mono" /></div>
          <div className="md:col-span-2"><Label>Conteúdo HTML (será sanitizado)</Label><Textarea name="conteudo" rows={6} /></div>
          <div className="md:col-span-2"><Button type="submit" loading={criar.isPending}>Publicar</Button></div>
        </form>
      </section>

      <section>
        <h2 className="text-2xl font-bold tracking-tighter mb-4">Disparar comunicação</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            disparar.mutate({
              titulo: String(fd.get('titulo')),
              corpo: String(fd.get('corpo')),
              finalidade: String(fd.get('finalidade')),
              segmentacao: {},
            });
            (e.target as HTMLFormElement).reset();
          }}
          className="grid grid-cols-1 md:grid-cols-2 gap-3"
        >
          <div><Label>Título</Label><Input name="titulo" required /></div>
          <div>
            <Label>Finalidade (opt-in verificado)</Label>
            <Select name="finalidade" defaultValue="novidades_plataforma">
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="novidades_plataforma">novidades_plataforma</SelectItem>
                <SelectItem value="conteudo_educativo">conteudo_educativo</SelectItem>
                <SelectItem value="comunicacao_prefeitura_municipio">prefeitura_municipio</SelectItem>
                <SelectItem value="comunicacao_orgao_estadual">orgao_estadual</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="md:col-span-2"><Label>Corpo</Label><Textarea name="corpo" required /></div>
          <div className="md:col-span-2"><Button type="submit" variant="accent" loading={disparar.isPending}>Disparar</Button></div>
        </form>
      </section>
    </div>
  );
}
