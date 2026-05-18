import { MapPin } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { MapSearch } from '@/components/MapSearch';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useAnuncio } from '@/hooks/useAnuncios';
import { useTipoMaterial } from '@/hooks/useCatalogo';
import { useAbrirNegociacao } from '@/hooks/useNegociacao';
import { formatBRL } from '@/utils/currency';
import { formatDate } from '@/utils/dates';

const CONDICAO_LABELS: Record<string, string> = {
  limpo: 'Limpo', sujo: 'Sujo', contaminado: 'Contaminado',
  seco: 'Seco', umido: 'Úmido', molhado: 'Molhado',
  solto: 'Solto', fardo: 'Fardo', prensado: 'Prensado',
  moido: 'Moído', triturado: 'Triturado', granulado: 'Granulado',
};

export default function AnuncioDetalhePage() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const { data, isLoading, error, refetch } = useAnuncio(id);
  const { data: tipo } = useTipoMaterial(data?.tipo_material_id ?? null);
  const abrir = useAbrirNegociacao();

  if (isLoading) return <AppLayout><CenterSpinner /></AppLayout>;
  if (error || !data) return <AppLayout><ErrorState onRetry={refetch} /></AppLayout>;

  // Anúncio identificado por Categoria > Subcategoria > Tipo + Condição
  const tituloDerivado = tipo?.nome ?? 'Anúncio de venda';

  const onNegociar = () => {
    abrir.mutate(
      { publicacao_id: data.id, publicacao_tipo: 'anuncio_venda' },
      {
        onSuccess: (neg) => navigate(`/negociacoes/${neg.id}`),
        onError: (err) =>
          showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Detalhe do anúncio" />
      <div className="pb-24">
        {data.fotos.length > 0 ? (
          <div className="aspect-[4/3] w-full overflow-hidden bg-neutral-100">
            <img src={data.fotos[0]} alt="" className="h-full w-full object-cover" />
          </div>
        ) : (
          <div className="aspect-[4/3] w-full bg-gradient-to-br from-primary-100 to-primary-300" />
        )}

        <div className="px-screen-x py-4 space-y-4">
          <div className="flex items-start justify-between gap-3">
            <h1 className="text-2xl font-bold tracking-tighter">{tituloDerivado}</h1>
            <StatusBadge status={data.status} />
          </div>

          <div className="rounded-xl bg-primary-50 p-4">
            <p className="text-xs uppercase tracking-wider text-primary-700">Preço pretendido</p>
            <p className="font-mono text-4xl font-bold text-primary-700">
              {formatBRL(data.preco_pretendido)}
              <span className="ml-1 text-sm font-normal text-primary-600">/{data.unidade}</span>
            </p>
          </div>

          {(data.condicao_limpeza || data.condicao_umidade || data.condicao_forma) && (
            <div className="flex flex-wrap gap-1.5">
              {[data.condicao_limpeza, data.condicao_umidade, data.condicao_forma]
                .filter(Boolean)
                .map((c) => (
                  <span
                    key={c}
                    className="rounded-full border border-primary-200 bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700"
                  >
                    {CONDICAO_LABELS[c as string] ?? c}
                  </span>
                ))}
            </div>
          )}

          {/* Atributos */}
          {Object.keys(data.atributos).length > 0 && (
            <div className="rounded-lg bg-surface-card border border-neutral-100 p-3 shadow-xs">
              <h3 className="mb-2 text-xs uppercase tracking-wider text-neutral-500">Características</h3>
              <dl className="grid grid-cols-2 gap-2 text-sm">
                {Object.entries(data.atributos).map(([k, v]) => (
                  <div key={k}>
                    <dt className="text-xs text-neutral-500">{k}</dt>
                    <dd className="text-neutral-900">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          <div>
            <div className="mb-1 flex items-center gap-1.5 text-sm text-neutral-700">
              <MapPin className="h-4 w-4" />
              <span>Localização aproximada · raio ~{Math.round(data.offset_m)}m</span>
            </div>
            <MapSearch
              center={{ lat: data.lat_pub, lng: data.lng_pub }}
              markers={[{ id: data.id, lat: data.lat_pub, lng: data.lng_pub, tipo: 'venda', titulo: tituloDerivado }]}
              height={220}
              zoom={14}
            />
            <p className="mt-1 text-[10px] text-neutral-500">
              Localização exata é liberada após aceite bilateral na Negociação.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-xs text-neutral-500">Frequência</p>
              <p className="font-semibold capitalize">{data.frequencia.replace('_', ' ')}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500">Válido até</p>
              <p className="font-mono">{formatDate(data.prazo_validade)}</p>
            </div>
          </div>
        </div>

        <div className="fixed bottom-20 left-1/2 z-tabbar w-full max-w-phone -translate-x-1/2 px-screen-x">
          <Button variant="primary" className="w-full" loading={abrir.isPending} onClick={onNegociar}>
            Iniciar negociação
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}
