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
import { showToast } from '@/components/ui/toaster';
import { useCriarFrete } from '@/hooks/useAnuncios';
import { useCategorias } from '@/hooks/useCatalogo';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

export default function CriarFretePage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { obterPosicao } = useGeolocalizacao();
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const { data: categorias } = useCategorias();
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);
  const [form, setForm] = useState({
    papel_id: '',
    tipo_veiculo: '',
    capacidade_t: '',
    raio: 200,
    emite_nf: false,
    prazo: toISOInputDate(new Date(Date.now() + 90 * 86400_000)),
    categoriasAceitas: [] as string[],
  });

  useEffect(() => {
    void obterPosicao().then(setLoc);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const criar = useCriarFrete();
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      {
        papel_id: form.papel_id,
        tipo_veiculo: form.tipo_veiculo,
        capacidade_t: form.capacidade_t ? Number(form.capacidade_t) : undefined,
        raio_operacional_km: form.raio,
        categorias_residuo_aceitas: form.categoriasAceitas,
        licencas: [],
        emite_nf: form.emite_nf,
        localizacao: loc,
        prazo_validade: new Date(form.prazo).toISOString(),
      },
      {
        onSuccess: () => {
          showToast({ title: 'Frete publicado', variant: 'success' });
          navigate('/fretes');
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  const papelFreteiro = papeis?.find((p) => p.papel === 'freteiro' && p.status === 'ativo');

  return (
    <AppLayout>
      <TopBar title="Novo frete" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <div>
          <Label>Papel (Freteiro)</Label>
          <Select value={form.papel_id} onValueChange={(v) => setForm({ ...form, papel_id: v })}>
            <SelectTrigger><SelectValue placeholder={papelFreteiro ? 'Selecione' : 'Ative o papel Freteiro primeiro'} /></SelectTrigger>
            <SelectContent>
              {papelFreteiro && <SelectItem value={papelFreteiro.id}>Freteiro</SelectItem>}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Tipo de veículo</Label>
            <Input
              required
              value={form.tipo_veiculo}
              onChange={(e) => setForm({ ...form, tipo_veiculo: e.target.value })}
              placeholder="VUC, Truck, Carreta..."
            />
          </div>
          <div>
            <Label>Capacidade (t)</Label>
            <Input
              type="number"
              step="0.1"
              value={form.capacidade_t}
              onChange={(e) => setForm({ ...form, capacidade_t: e.target.value })}
              className="font-mono"
            />
          </div>
        </div>

        <div>
          <Label>Raio operacional (km)</Label>
          <Input
            type="number"
            min={1}
            required
            value={form.raio}
            onChange={(e) => setForm({ ...form, raio: Number(e.target.value) })}
            className="font-mono"
          />
        </div>

        <div>
          <Label>Categorias de resíduo aceitas</Label>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {categorias?.map((c) => {
              const checked = form.categoriasAceitas.includes(c.slug);
              return (
                <label key={c.id} className="flex items-center gap-2 rounded-lg border border-neutral-200 p-2 text-sm">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...form.categoriasAceitas, c.slug]
                        : form.categoriasAceitas.filter((s) => s !== c.slug);
                      setForm({ ...form, categoriasAceitas: next });
                    }}
                  />
                  {c.nome}
                </label>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-between rounded-lg border border-neutral-200 p-3">
          <p className="text-sm font-semibold">Emite Nota Fiscal</p>
          <Switch checked={form.emite_nf} onCheckedChange={(v) => setForm({ ...form, emite_nf: v })} />
        </div>

        <div>
          <Label>Base operacional</Label>
          <MapPicker value={loc} onChange={setLoc} height={240} />
        </div>

        <div>
          <Label>Prazo</Label>
          <Input
            type="date"
            required
            value={form.prazo}
            onChange={(e) => setForm({ ...form, prazo: e.target.value })}
          />
        </div>

        <Button type="submit" loading={criar.isPending} className="w-full">Publicar frete</Button>
      </form>
    </AppLayout>
  );
}
