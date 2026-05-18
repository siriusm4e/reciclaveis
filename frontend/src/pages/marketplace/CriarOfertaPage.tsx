import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { ConditionSelector } from '@/components/ConditionSelector';
import { MapPicker } from '@/components/MapPicker';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { showToast } from '@/components/ui/toaster';
import { useCriarOferta } from '@/hooks/useAnuncios';
import { useCategorias, useSubcategorias, useTiposMaterial } from '@/hooks/useCatalogo';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import type { CondicaoForma, CondicaoLimpeza, CondicaoUmidade } from '@/types/api';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

export default function CriarOfertaPage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { obterPosicao } = useGeolocalizacao();
  const { data: categorias } = useCategorias();
  const { data: papeis } = usePapeis(conta?.id ?? null);

  const [categoriaId, setCategoriaId] = useState('');
  const [subcategoriaId, setSubcategoriaId] = useState('');
  const [tipoMaterialId, setTipoMaterialId] = useState('');
  const { data: subs } = useSubcategorias(categoriaId || null);
  const { data: tipos } = useTiposMaterial(subcategoriaId || null);

  useEffect(() => {
    setSubcategoriaId('');
    setTipoMaterialId('');
  }, [categoriaId]);
  useEffect(() => {
    setTipoMaterialId('');
  }, [subcategoriaId]);

  const tipoSelecionado = tipos?.find((t) => t.id === tipoMaterialId);

  const [form, setForm] = useState({
    papel_id: '',
    titulo: '',
    descricao: '',
    preco_paga: '',
    unidade: 'kg',
    volume_min: '',
    volume_max: '',
    volume_minimo_kg: '',
    raio_km: 25,
    retira: false,
    prazo_validade: toISOInputDate(new Date(Date.now() + 30 * 86400_000)),
  });
  const [condicaoLimpeza, setCondicaoLimpeza] = useState<CondicaoLimpeza | null>(null);
  const [condicaoUmidade, setCondicaoUmidade] = useState<CondicaoUmidade | null>(null);
  const [condicaoForma, setCondicaoForma] = useState<CondicaoForma | null>(null);
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);

  useEffect(() => {
    void obterPosicao().then((p) => setLoc(p));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (tipoSelecionado) setForm((f) => ({ ...f, unidade: tipoSelecionado.unidade_padrao }));
  }, [tipoSelecionado]);

  const criar = useCriarOferta();
  const tipoEscolhido = Boolean(tipoMaterialId);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.papel_id || !tipoMaterialId) {
      showToast({ title: 'Selecione Papel, Categoria, Subcategoria e Tipo', variant: 'warning' });
      return;
    }
    criar.mutate(
      {
        papel_id: form.papel_id,
        tipo_material_id: tipoMaterialId,
        titulo: form.titulo,
        descricao: form.descricao || undefined,
        especificacao: {},
        preco_paga: Number(form.preco_paga),
        unidade: form.unidade,
        volume_min: Number(form.volume_min),
        volume_max: form.volume_max ? Number(form.volume_max) : undefined,
        volume_minimo_kg: form.volume_minimo_kg ? Number(form.volume_minimo_kg) : undefined,
        condicao_limpeza: condicaoLimpeza ?? undefined,
        condicao_umidade: condicaoUmidade ?? undefined,
        condicao_forma: condicaoForma ?? undefined,
        localizacao: loc,
        raio_km: form.raio_km,
        retira: form.retira,
        prazo_validade: new Date(form.prazo_validade).toISOString(),
      },
      {
        onSuccess: (o) => {
          showToast({ title: 'Oferta publicada', variant: 'success' });
          navigate(`/ofertas/${o.id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  const papeisAtivos = papeis?.filter((p) => p.status === 'ativo') ?? [];

  return (
    <AppLayout>
      <TopBar title="Nova oferta de compra" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <div>
          <Label>Papel</Label>
          <Select value={form.papel_id} onValueChange={(v) => setForm({ ...form, papel_id: v })}>
            <SelectTrigger><SelectValue placeholder="Escolha um papel ativo" /></SelectTrigger>
            <SelectContent>
              {papeisAtivos.map((p) => (
                <SelectItem key={p.id} value={p.id}>{p.papel.replace('_', ' ')}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* === 3 dropdowns encadeados === */}
        <div className="space-y-3">
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
            <Select value={subcategoriaId} onValueChange={setSubcategoriaId} disabled={!categoriaId}>
              <SelectTrigger>
                <SelectValue placeholder={categoriaId ? 'Selecione' : 'Escolha uma categoria primeiro'} />
              </SelectTrigger>
              <SelectContent>
                {subs?.map((s) => (
                  <SelectItem key={s.id} value={s.id}>{s.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Tipo de Material</Label>
            <Select value={tipoMaterialId} onValueChange={setTipoMaterialId} disabled={!subcategoriaId}>
              <SelectTrigger>
                <SelectValue placeholder={subcategoriaId ? 'Selecione' : 'Escolha uma subcategoria primeiro'} />
              </SelectTrigger>
              <SelectContent>
                {tipos?.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className={tipoEscolhido ? '' : 'pointer-events-none opacity-40'} aria-disabled={!tipoEscolhido}>
          <Input
            required={tipoEscolhido}
            minLength={3}
            placeholder="Título da demanda"
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
          />

          <Textarea
            placeholder="Especificações detalhadas"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            className="mt-3"
          />

          {/* === Condição buscada === */}
          <div className="space-y-3 rounded-lg border border-neutral-200 p-3 mt-3">
            <p className="text-sm font-semibold text-neutral-800">Condição buscada (opcional)</p>
            <ConditionSelector group="limpeza" value={condicaoLimpeza} onChange={setCondicaoLimpeza} />
            <ConditionSelector group="umidade" value={condicaoUmidade} onChange={setCondicaoUmidade} />
            <ConditionSelector group="forma" value={condicaoForma} onChange={setCondicaoForma} />
          </div>

          <div className="grid grid-cols-2 gap-3 mt-3">
            <div>
              <Label>Preço pago (R$)</Label>
              <Input
                type="number"
                step="0.01"
                required={tipoEscolhido}
                value={form.preco_paga}
                onChange={(e) => setForm({ ...form, preco_paga: e.target.value })}
                className="font-mono"
              />
            </div>
            <div>
              <Label>Unidade</Label>
              <Input value={form.unidade} onChange={(e) => setForm({ ...form, unidade: e.target.value })} />
            </div>
            <div>
              <Label>Volume mín.</Label>
              <Input
                type="number"
                required={tipoEscolhido}
                value={form.volume_min}
                onChange={(e) => setForm({ ...form, volume_min: e.target.value })}
                className="font-mono"
              />
            </div>
            <div>
              <Label>Volume máx. (opcional)</Label>
              <Input
                type="number"
                value={form.volume_max}
                onChange={(e) => setForm({ ...form, volume_max: e.target.value })}
                className="font-mono"
              />
            </div>
          </div>

          {/* === Filtro mútuo de visibilidade === */}
          <div className="mt-3 rounded-lg bg-neutral-50 border border-neutral-200 p-3">
            <Label htmlFor="volmin">Volume mínimo do vendedor (kg) — filtro de visibilidade</Label>
            <Input
              id="volmin"
              type="number"
              min={0}
              placeholder="ex.: 30 (vazio = sem restrição)"
              value={form.volume_minimo_kg}
              onChange={(e) => setForm({ ...form, volume_minimo_kg: e.target.value })}
              className="font-mono"
            />
            <p className="mt-1 text-[11px] text-neutral-500">
              Vendedores com volume estimado abaixo deste número não verão sua oferta — e você não os verá.
            </p>
          </div>

          {/* === Raio (slider 1-500km) === */}
          <div className="mt-3">
            <div className="flex items-baseline justify-between">
              <Label>Raio de busca</Label>
              <span className="font-mono text-sm font-semibold text-accent-600">{form.raio_km} km</span>
            </div>
            <input
              type="range"
              min={1}
              max={500}
              step={1}
              value={form.raio_km}
              onChange={(e) => setForm({ ...form, raio_km: Number(e.target.value) })}
              className="w-full accent-accent-500"
              aria-label="Raio em km, mínimo 1, máximo 500"
            />
            <div className="flex justify-between text-[10px] text-neutral-500">
              <span>1 km</span>
              <span>500 km</span>
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between rounded-lg border border-neutral-200 p-3">
            <div>
              <p className="text-sm font-semibold">Eu retiro o material</p>
              <p className="text-xs text-neutral-500">Comprador busca no local do vendedor</p>
            </div>
            <Switch checked={form.retira} onCheckedChange={(v) => setForm({ ...form, retira: v })} />
          </div>

          <div className="mt-3">
            <Label>Localização do comprador</Label>
            <MapPicker value={loc} onChange={setLoc} height={240} />
          </div>

          <div className="mt-3">
            <Label>Válido até</Label>
            <Input
              type="date"
              required={tipoEscolhido}
              value={form.prazo_validade}
              onChange={(e) => setForm({ ...form, prazo_validade: e.target.value })}
            />
          </div>
        </div>

        <Button
          type="submit"
          loading={criar.isPending}
          variant="accent"
          disabled={!tipoEscolhido}
          className="w-full"
        >
          {tipoEscolhido ? 'Publicar oferta de compra' : 'Selecione Tipo de Material para continuar'}
        </Button>
      </form>
    </AppLayout>
  );
}
