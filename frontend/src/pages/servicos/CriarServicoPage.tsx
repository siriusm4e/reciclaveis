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
import { useCriarServico } from '@/hooks/useAnuncios';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

export default function CriarServicoPage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { obterPosicao } = useGeolocalizacao();
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);

  const [form, setForm] = useState({
    papel_id: '',
    tipo_servico: '',
    descricao: '',
    raio: 50,
    unidade: 'visita' as 'hora' | 'visita' | 'lote',
    preco: '',
    prazo: toISOInputDate(new Date(Date.now() + 90 * 86400_000)),
  });

  useEffect(() => {
    void obterPosicao().then(setLoc);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const criar = useCriarServico();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      {
        papel_id: form.papel_id,
        tipo_servico: form.tipo_servico,
        descricao: form.descricao || undefined,
        raio_operacional_km: form.raio,
        unidade_cobranca: form.unidade,
        preco: form.preco ? Number(form.preco) : undefined,
        localizacao: loc,
        prazo_validade: new Date(form.prazo).toISOString(),
      },
      {
        onSuccess: (s) => {
          showToast({ title: 'Serviço publicado', variant: 'success' });
          navigate(`/servicos/${s.id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  const papeisAtivos = papeis?.filter((p) => p.status === 'ativo') ?? [];

  return (
    <AppLayout>
      <TopBar title="Novo serviço" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <div>
          <Label>Papel</Label>
          <Select value={form.papel_id} onValueChange={(v) => setForm({ ...form, papel_id: v })}>
            <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
            <SelectContent>
              {papeisAtivos.map((p) => (
                <SelectItem key={p.id} value={p.id}>{p.papel.replace('_', ' ')}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Input
          placeholder="Tipo de serviço (ex.: Manutenção, Consultoria)"
          required
          value={form.tipo_servico}
          onChange={(e) => setForm({ ...form, tipo_servico: e.target.value })}
        />
        <Textarea
          placeholder="Descrição"
          value={form.descricao}
          onChange={(e) => setForm({ ...form, descricao: e.target.value })}
        />
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Raio (km)</Label>
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
            <Label>Cobrança</Label>
            <Select value={form.unidade} onValueChange={(v) => setForm({ ...form, unidade: v as 'hora' | 'visita' | 'lote' })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="hora">Por hora</SelectItem>
                <SelectItem value="visita">Por visita</SelectItem>
                <SelectItem value="lote">Por lote</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Preço (R$, opcional)</Label>
            <Input
              type="number"
              step="0.01"
              value={form.preco}
              onChange={(e) => setForm({ ...form, preco: e.target.value })}
              className="font-mono"
            />
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
        </div>
        <div>
          <Label>Localização (centro do raio)</Label>
          <MapPicker value={loc} onChange={setLoc} height={240} />
        </div>
        <Button type="submit" loading={criar.isPending} className="w-full">Publicar serviço</Button>
      </form>
    </AppLayout>
  );
}
