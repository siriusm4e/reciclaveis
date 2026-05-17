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
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { showToast } from '@/components/ui/toaster';
import { useCriarOferta } from '@/hooks/useAnuncios';
import { useCategorias, useSubcategorias } from '@/hooks/useCatalogo';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

export default function CriarOfertaPage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { obterPosicao } = useGeolocalizacao();
  const { data: categorias } = useCategorias();
  const { data: papeis } = usePapeis(conta?.id ?? null);

  const [categoriaId, setCategoriaId] = useState('');
  const { data: subs } = useSubcategorias(categoriaId || null);

  const [form, setForm] = useState({
    papel_id: '',
    subcategoria_id: '',
    titulo: '',
    descricao: '',
    preco_paga: '',
    unidade: 'kg',
    volume_min: '',
    volume_max: '',
    raio_km: 25,
    retira: false,
    prazo_validade: toISOInputDate(new Date(Date.now() + 30 * 86400_000)),
  });
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);

  useEffect(() => {
    void obterPosicao().then((p) => setLoc(p));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const criar = useCriarOferta();

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
        especificacao: {},
        preco_paga: Number(form.preco_paga),
        unidade: form.unidade,
        volume_min: Number(form.volume_min),
        volume_max: form.volume_max ? Number(form.volume_max) : undefined,
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
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {subs?.map((s) => (
                  <SelectItem key={s.id} value={s.id}>{s.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Input
          required
          minLength={3}
          placeholder="Título da demanda"
          value={form.titulo}
          onChange={(e) => setForm({ ...form, titulo: e.target.value })}
        />

        <Textarea
          placeholder="Especificações detalhadas"
          value={form.descricao}
          onChange={(e) => setForm({ ...form, descricao: e.target.value })}
        />

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Preço pago (R$)</Label>
            <Input
              type="number"
              step="0.01"
              required
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
              required
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

        <div>
          <Label>Raio (km)</Label>
          <Input
            type="number"
            min={1}
            max={500}
            value={form.raio_km}
            onChange={(e) => setForm({ ...form, raio_km: Number(e.target.value) })}
            className="font-mono"
          />
        </div>

        <div className="flex items-center justify-between rounded-lg border border-neutral-200 p-3">
          <div>
            <p className="text-sm font-semibold">Eu retiro o material</p>
            <p className="text-xs text-neutral-500">Comprador busca no local do vendedor</p>
          </div>
          <Switch checked={form.retira} onCheckedChange={(v) => setForm({ ...form, retira: v })} />
        </div>

        <div>
          <Label>Localização do comprador</Label>
          <MapPicker value={loc} onChange={setLoc} height={240} />
        </div>

        <div>
          <Label>Válido até</Label>
          <Input
            type="date"
            required
            value={form.prazo_validade}
            onChange={(e) => setForm({ ...form, prazo_validade: e.target.value })}
          />
        </div>

        <Button type="submit" loading={criar.isPending} variant="accent" className="w-full">
          Publicar oferta de compra
        </Button>
      </form>
    </AppLayout>
  );
}
