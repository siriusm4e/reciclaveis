import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { useAtivarAlertaPago, useOferta } from '@/hooks/useAnuncios';
import { useSaldoCreditos } from '@/hooks/useCreditos';
import { formatNumber } from '@/utils/currency';

export default function AlertaPagoPage() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const { data: oferta } = useOferta(id);
  const { data: saldo } = useSaldoCreditos();
  const [raio, setRaio] = useState(50);
  const [horas, setHoras] = useState(24);

  const ativar = useAtivarAlertaPago(id);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    ativar.mutate(
      { raio_km: raio, duracao_horas: horas, segmentacao: {} },
      {
        onSuccess: (res) => {
          if (!res.disparou) {
            showToast({
              title: 'Cobertura insuficiente',
              description: `Apenas ${res.cobertura} vendedores elegíveis (mín. ${res.cobertura_minima}). Seus créditos foram devolvidos.`,
              variant: 'warning',
            });
          } else {
            showToast({
              title: 'Alerta enviado',
              description: `${res.cobertura} vendedores notificados.`,
              variant: 'success',
            });
          }
          navigate(`/ofertas/${id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Alerta Pago" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4">
        <div className="rounded-xl bg-accent-500/10 p-4">
          <p className="text-xs uppercase tracking-wider text-accent-600">Saldo de Créditos</p>
          <p className="font-mono text-3xl font-bold text-accent-600">{formatNumber(saldo?.saldo ?? 0)}</p>
          <p className="mt-1 text-sm text-neutral-700">
            Custo do disparo: <span className="font-mono">10</span> créditos.
            Se a cobertura for insuficiente, os créditos são reembolsados.
          </p>
        </div>

        <div>
          <Label>Raio do alerta (km)</Label>
          <Input
            type="number"
            min={1}
            max={500}
            value={raio}
            onChange={(e) => setRaio(Number(e.target.value))}
            className="font-mono"
          />
        </div>
        <div>
          <Label>Duração (horas)</Label>
          <Input
            type="number"
            min={1}
            max={168}
            value={horas}
            onChange={(e) => setHoras(Number(e.target.value))}
            className="font-mono"
          />
        </div>

        <Button type="submit" loading={ativar.isPending} variant="accent" className="w-full" disabled={!oferta}>
          Ativar boost
        </Button>
      </form>
    </AppLayout>
  );
}
