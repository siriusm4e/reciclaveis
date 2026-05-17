import { useEffect, useState } from 'react';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { MapPicker } from '@/components/MapPicker';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useCriarPedidoColeta, usePedidosColeta } from '@/hooks/useInstitucional';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';

export default function PedidoColetaPage() {
  const { obterPosicao } = useGeolocalizacao();
  const { data: lista, isLoading } = usePedidosColeta();
  const criar = useCriarPedidoColeta();
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);
  const [form, setForm] = useState({
    bairro: '',
    cidade: '',
    uf: 'SP',
    tipo: '',
    descricao: '',
  });

  useEffect(() => {
    void obterPosicao().then(setLoc);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      {
        bairro: form.bairro,
        cidade: form.cidade,
        uf: form.uf.toUpperCase(),
        tipo_residuo: form.tipo,
        descricao: form.descricao || undefined,
        localizacao: loc,
      },
      {
        onSuccess: () => {
          showToast({ title: 'Pedido enviado', variant: 'success' });
          setForm({ bairro: '', cidade: '', uf: 'SP', tipo: '', descricao: '' });
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Coleta pública" />
      <div className="px-screen-x py-4 space-y-4">
        <form onSubmit={onSubmit} className="space-y-3 rounded-lg bg-surface-card border border-neutral-100 p-4 shadow-xs">
          <h3 className="font-bold tracking-tight">Solicitar coleta</h3>
          <div className="grid grid-cols-2 gap-3">
            <Input required placeholder="Bairro" value={form.bairro} onChange={(e) => setForm({ ...form, bairro: e.target.value })} />
            <Input required placeholder="Cidade" value={form.cidade} onChange={(e) => setForm({ ...form, cidade: e.target.value })} />
            <Input
              required
              maxLength={2}
              placeholder="UF"
              value={form.uf}
              onChange={(e) => setForm({ ...form, uf: e.target.value.toUpperCase() })}
              className="uppercase font-mono"
            />
            <Input required placeholder="Tipo de resíduo" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} />
          </div>
          <Textarea placeholder="Descrição (opcional)" value={form.descricao} onChange={(e) => setForm({ ...form, descricao: e.target.value })} />
          <div>
            <Label>Local</Label>
            <MapPicker value={loc} onChange={setLoc} height={200} />
          </div>
          <Button type="submit" loading={criar.isPending} className="w-full">Enviar pedido</Button>
        </form>

        <div>
          <h3 className="text-sm font-bold tracking-tight mb-2">Meus pedidos</h3>
          {isLoading ? (
            <CenterSpinner />
          ) : !lista?.length ? (
            <EmptyState titulo="Sem pedidos" />
          ) : (
            <div className="space-y-2">
              {lista.map((p) => (
                <Card key={p.id} className="p-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-semibold">{p.tipo_residuo}</p>
                      <p className="text-xs text-neutral-500">{p.bairro} · {p.cidade}/{p.uf}</p>
                    </div>
                    <StatusBadge status={p.status} />
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
