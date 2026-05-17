import { Sparkles } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { MapSearch } from '@/components/MapSearch';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useOferta } from '@/hooks/useAnuncios';
import { useAbrirNegociacao } from '@/hooks/useNegociacao';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import { formatBRL, formatNumber } from '@/utils/currency';
import { formatDate } from '@/utils/dates';

export default function OfertaDetalhePage() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { data, isLoading, error, refetch } = useOferta(id);
  const abrir = useAbrirNegociacao();

  if (isLoading) return <AppLayout><CenterSpinner /></AppLayout>;
  if (error || !data) return <AppLayout><ErrorState onRetry={refetch} /></AppLayout>;

  const ehDoUsuario = conta?.id === data.conta_id;

  const onNegociar = () => {
    abrir.mutate(
      { publicacao_id: data.id, publicacao_tipo: 'oferta_compra' },
      {
        onSuccess: (neg) => navigate(`/negociacoes/${neg.id}`),
        onError: (err) =>
          showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Oferta de compra" />
      <div className="px-screen-x py-4 space-y-4 pb-32">
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-2xl font-bold tracking-tighter">{data.titulo}</h1>
          <StatusBadge status={data.status} />
        </div>

        {data.boost_ativo && (
          <div className="flex items-center gap-2 rounded-lg bg-accent-500/15 px-3 py-2 text-accent-600">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-semibold">Alerta Pago ativo</span>
          </div>
        )}

        <div className="rounded-xl bg-accent-500/10 p-4">
          <p className="text-xs uppercase tracking-wider text-accent-600">Compra por</p>
          <p className="font-mono text-4xl font-bold text-accent-600">
            {formatBRL(data.preco_paga)}
            <span className="ml-1 text-sm font-normal">/{data.unidade}</span>
          </p>
          <p className="mt-1 text-sm text-neutral-700">
            Volume mín: <span className="font-mono">{formatNumber(data.volume_min)}</span>
            {data.volume_max && (
              <> · Máx: <span className="font-mono">{formatNumber(data.volume_max)}</span></>
            )}
            {' '}{data.unidade}
          </p>
        </div>

        {data.descricao && (
          <p className="font-serif italic text-base text-neutral-700">{data.descricao}</p>
        )}

        <div>
          <p className="mb-1 text-sm text-neutral-700">
            Raio de busca: <span className="font-mono">{data.raio_km}km</span>
            {data.retira && <> · O comprador <strong>retira</strong></>}
          </p>
          <MapSearch
            center={{ lat: data.lat, lng: data.lng }}
            markers={[{ id: data.id, lat: data.lat, lng: data.lng, tipo: 'compra', titulo: data.titulo }]}
            height={220}
            zoom={12}
          />
        </div>

        <div>
          <p className="text-xs text-neutral-500">Válido até</p>
          <p className="font-mono">{formatDate(data.prazo_validade)}</p>
        </div>

        <div className="fixed bottom-20 left-1/2 z-tabbar w-full max-w-phone -translate-x-1/2 px-screen-x space-y-2">
          {ehDoUsuario ? (
            <>
              <Button variant="accent" className="w-full" onClick={() => navigate(`/ofertas/${data.id}/alerta-pago`)}>
                Configurar Alerta Pago
              </Button>
            </>
          ) : (
            <Button variant="accent" className="w-full" loading={abrir.isPending} onClick={onNegociar}>
              Oferecer material
            </Button>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
