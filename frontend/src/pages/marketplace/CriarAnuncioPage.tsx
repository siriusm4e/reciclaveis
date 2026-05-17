import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { MapPicker } from '@/components/MapPicker';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { showToast } from '@/components/ui/toaster';
import { useCriarAnuncio } from '@/hooks/useAnuncios';
import { useCategorias, useSubcategorias } from '@/hooks/useCatalogo';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

export default function CriarAnuncioPage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { obterPosicao } = useGeolocalizacao();
  const { data: categorias } = useCategorias();
  const { data: papeis } = usePapeis(conta?.id ?? null);

  const [categoriaId, setCategoriaId] = useState<string>('');
  const { data: subcategorias } = useSubcategorias(categoriaId || null);

  const [form, setForm] = useState({
    papel_id: '',
    subcategoria_id: '',
    titulo: '',
    descricao: '',
    preco_pretendido: '',
    unidade: 'kg',
    volume_estimado: '',
    territorio: 'urbano' as 'urbano' | 'rural',
    frequencia: 'lote_unico' as 'lote_unico' | 'recorrente',
    intervalo_geracao: '',
    prazo_validade: toISOInputDate(new Date(Date.now() + 30 * 86400_000)),
  });
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);

  useEffect(() => {
    void obterPosicao().then((p) => setLoc(p));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const subSelecionada = subcategorias?.find((s) => s.id === form.subcategoria_id);
  useEffect(() => {
    if (subSelecionada) setForm((f) => ({ ...f, unidade: subSelecionada.unidade_padrao }));
  }, [subSelecionada]);

  const criar = useCriarAnuncio();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.papel_id || !form.subcategoria_id) {
      showToast({ title: 'Selecione Papel e Subcategoria', variant: 'warning' });
      return;
    }
    criar.mutate(
      {
        papel_id: form.papel_id,
        subcategoria_id: form.subcategoria_id,
        titulo: form.titulo,
        descricao: form.descricao || undefined,
        atributos: {},
        localizacao_real: loc,
        territorio: form.territorio,
        preco_pretendido: Number(form.preco_pretendido),
        unidade: form.unidade,
        volume_estimado: form.volume_estimado ? Number(form.volume_estimado) : undefined,
        frequencia: form.frequencia,
        intervalo_geracao: form.frequencia === 'recorrente' ? form.intervalo_geracao : undefined,
        prazo_validade: new Date(form.prazo_validade).toISOString(),
        fotos: [],
      },
      {
        onSuccess: (a) => {
          showToast({ title: 'Anúncio publicado', variant: 'success' });
          navigate(`/anuncios/${a.id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  const papelAtivos = papeis?.filter((p) => p.status === 'ativo') ?? [];

  return (
    <AppLayout>
      <TopBar title="Novo anúncio de venda" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <div>
          <Label>Papel que está publicando</Label>
          <Select value={form.papel_id} onValueChange={(v) => setForm({ ...form, papel_id: v })}>
            <SelectTrigger><SelectValue placeholder="Escolha um papel ativo" /></SelectTrigger>
            <SelectContent>
              {papelAtivos.length === 0 ? (
                <SelectItem value="_" disabled>Sem papéis ativos — ative em Perfil</SelectItem>
              ) : (
                papelAtivos.map((p) => (
                  <SelectItem key={p.id} value={p.id}>{p.papel.replace('_', ' ')}</SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Categoria</Label>
            <Select value={categoriaId} onValueChange={setCategoriaId}>
              <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
              <SelectContent>
                {categorias?.map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Subcategoria</Label>
            <Select
              value={form.subcategoria_id}
              onValueChange={(v) => setForm({ ...form, subcategoria_id: v })}
              disabled={!categoriaId}
            >
              <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
              <SelectContent>
                {subcategorias?.map((s) => (
                  <SelectItem key={s.id} value={s.id}>{s.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {subSelecionada?.requer_validacao_documental && (
          <div className="rounded-lg bg-warning-light p-2 text-xs text-warning-dark">
            Subcategoria regulada — exige documentos aprovados:{' '}
            <span className="font-mono">{subSelecionada.documentos_exigidos.join(', ')}</span>
          </div>
        )}

        <div>
          <Label htmlFor="titulo">Título</Label>
          <Input
            id="titulo"
            required
            minLength={3}
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
          />
        </div>

        <div>
          <Label htmlFor="desc">Descrição</Label>
          <Textarea
            id="desc"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            placeholder="Estado, limpeza, observações..."
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="preco">Preço (R$)</Label>
            <Input
              id="preco"
              type="number"
              step="0.01"
              min="0"
              required
              value={form.preco_pretendido}
              onChange={(e) => setForm({ ...form, preco_pretendido: e.target.value })}
              className="font-mono"
            />
          </div>
          <div>
            <Label htmlFor="unidade">Unidade</Label>
            <Input
              id="unidade"
              value={form.unidade}
              onChange={(e) => setForm({ ...form, unidade: e.target.value })}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Frequência</Label>
            <Select value={form.frequencia} onValueChange={(v) => setForm({ ...form, frequencia: v as 'lote_unico' | 'recorrente' })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="lote_unico">Lote único</SelectItem>
                <SelectItem value="recorrente">Recorrente</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Território</Label>
            <Select value={form.territorio} onValueChange={(v) => setForm({ ...form, territorio: v as 'urbano' | 'rural' })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="urbano">Urbano</SelectItem>
                <SelectItem value="rural">Rural</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {form.frequencia === 'recorrente' && (
          <div>
            <Label htmlFor="intervalo">Intervalo</Label>
            <Input
              id="intervalo"
              required
              placeholder="ex.: semanal, mensal"
              value={form.intervalo_geracao}
              onChange={(e) => setForm({ ...form, intervalo_geracao: e.target.value })}
            />
          </div>
        )}

        <div>
          <Label htmlFor="prazo">Válido até</Label>
          <Input
            id="prazo"
            type="date"
            required
            value={form.prazo_validade}
            onChange={(e) => setForm({ ...form, prazo_validade: e.target.value })}
          />
        </div>

        <div>
          <Label>Localização (arraste o pin)</Label>
          <MapPicker value={loc} onChange={setLoc} height={240} />
          <p className="mt-1 text-[10px] text-neutral-500">
            Será publicada com offset de privacidade ({form.territorio === 'urbano' ? '~250m' : '~1.5km'}).
          </p>
        </div>

        <Button type="submit" loading={criar.isPending} className="w-full">Publicar anúncio</Button>
      </form>
    </AppLayout>
  );
}
