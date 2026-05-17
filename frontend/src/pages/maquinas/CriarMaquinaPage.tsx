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
import { useCriarMaquina } from '@/hooks/useAnuncios';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

export default function CriarMaquinaPage() {
  const navigate = useNavigate();
  const { obterPosicao } = useGeolocalizacao();
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);
  const [form, setForm] = useState({
    categoria_equipamento: '',
    marca: '',
    modelo: '',
    ano: '',
    capacidade: '',
    descricao: '',
    condicao: 'usado' as 'novo' | 'seminovo' | 'usado',
    modalidade: 'venda' as 'venda' | 'aluguel' | 'ambos',
    preco: '',
    prazo: toISOInputDate(new Date(Date.now() + 60 * 86400_000)),
  });

  useEffect(() => {
    void obterPosicao().then(setLoc);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const criar = useCriarMaquina();
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      {
        categoria_equipamento: form.categoria_equipamento,
        marca: form.marca || undefined,
        modelo: form.modelo || undefined,
        ano: form.ano ? Number(form.ano) : undefined,
        capacidade: form.capacidade || undefined,
        descricao: form.descricao || undefined,
        condicao: form.condicao,
        modalidade: form.modalidade,
        disponibilidade: form.modalidade !== 'venda' ? { dias: ['seg', 'ter', 'qua', 'qui', 'sex'] } : undefined,
        preco: Number(form.preco),
        fotos: [],
        localizacao: loc,
        prazo_validade: new Date(form.prazo).toISOString(),
      },
      {
        onSuccess: (m) => {
          showToast({ title: 'Equipamento publicado', variant: 'success' });
          navigate(`/maquinas/${m.id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Novo equipamento" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <div>
          <Label>Categoria do equipamento</Label>
          <Input
            required
            value={form.categoria_equipamento}
            onChange={(e) => setForm({ ...form, categoria_equipamento: e.target.value })}
            placeholder="Ex.: Prensa, Empilhadeira, Triturador"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Marca</Label>
            <Input value={form.marca} onChange={(e) => setForm({ ...form, marca: e.target.value })} />
          </div>
          <div>
            <Label>Modelo</Label>
            <Input value={form.modelo} onChange={(e) => setForm({ ...form, modelo: e.target.value })} />
          </div>
          <div>
            <Label>Ano</Label>
            <Input
              type="number"
              value={form.ano}
              onChange={(e) => setForm({ ...form, ano: e.target.value })}
              className="font-mono"
            />
          </div>
          <div>
            <Label>Capacidade</Label>
            <Input value={form.capacidade} onChange={(e) => setForm({ ...form, capacidade: e.target.value })} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Condição</Label>
            <Select value={form.condicao} onValueChange={(v) => setForm({ ...form, condicao: v as 'novo' | 'seminovo' | 'usado' })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="novo">Novo</SelectItem>
                <SelectItem value="seminovo">Seminovo</SelectItem>
                <SelectItem value="usado">Usado</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Modalidade</Label>
            <Select value={form.modalidade} onValueChange={(v) => setForm({ ...form, modalidade: v as 'venda' | 'aluguel' | 'ambos' })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="venda">Venda</SelectItem>
                <SelectItem value="aluguel">Aluguel</SelectItem>
                <SelectItem value="ambos">Venda e aluguel</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <Label>Preço (R$)</Label>
          <Input
            type="number"
            step="0.01"
            required
            value={form.preco}
            onChange={(e) => setForm({ ...form, preco: e.target.value })}
            className="font-mono"
          />
        </div>

        <Textarea
          placeholder="Descrição do equipamento"
          value={form.descricao}
          onChange={(e) => setForm({ ...form, descricao: e.target.value })}
        />

        <div>
          <Label>Local do equipamento</Label>
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

        <Button type="submit" loading={criar.isPending} className="w-full">Publicar equipamento</Button>
      </form>
    </AppLayout>
  );
}
