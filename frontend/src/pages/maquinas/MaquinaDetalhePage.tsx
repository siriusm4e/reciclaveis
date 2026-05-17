import { useParams } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { MapSearch } from '@/components/MapSearch';
import { TopBar } from '@/components/TopBar';
import { CenterSpinner, EmptyState, ErrorState } from '@/components/ui/states';
import { useManutencaoProxima, useMaquina } from '@/hooks/useAnuncios';
import { formatBRL } from '@/utils/currency';

export default function MaquinaDetalhePage() {
  const { id = '' } = useParams();
  const { data, isLoading, error, refetch } = useMaquina(id);
  const manut = useManutencaoProxima(id);

  if (isLoading) return <AppLayout><CenterSpinner /></AppLayout>;
  if (error || !data) return <AppLayout><ErrorState onRetry={refetch} /></AppLayout>;

  return (
    <AppLayout>
      <TopBar title={data.modelo ?? data.categoria_equipamento} />
      <div className="px-screen-x py-4 space-y-4 pb-12">
        <div className="aspect-[4/3] w-full overflow-hidden rounded-lg bg-neutral-100">
          {data.fotos[0] ? (
            <img src={data.fotos[0]} alt="" className="h-full w-full object-cover" />
          ) : (
            <div className="h-full w-full bg-gradient-to-br from-neutral-200 to-neutral-400" />
          )}
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-neutral-500">{data.marca}</p>
          <h1 className="text-2xl font-bold tracking-tighter">{data.modelo ?? data.categoria_equipamento}</h1>
          <p className="font-mono text-3xl font-bold text-primary-700 mt-2">{formatBRL(data.preco)}</p>
          <p className="text-xs text-neutral-500 uppercase tracking-wider">{data.modalidade} · {data.condicao}</p>
        </div>

        {data.descricao && <p className="font-serif italic text-neutral-700">{data.descricao}</p>}

        <div>
          <h3 className="mb-1 text-sm font-semibold">Localização</h3>
          <MapSearch
            center={{ lat: data.lat, lng: data.lng }}
            markers={[{ id: data.id, lat: data.lat, lng: data.lng, tipo: 'venda', titulo: data.categoria_equipamento }]}
            height={200}
            zoom={12}
          />
        </div>

        <div>
          <h3 className="mb-2 text-sm font-semibold">Manutenção próxima (50km)</h3>
          {manut.isLoading ? (
            <p className="text-sm text-neutral-500">Buscando prestadores...</p>
          ) : !manut.data?.length ? (
            <EmptyState titulo="Sem prestadores de manutenção próximos" />
          ) : (
            <div className="space-y-2">
              {(manut.data as Array<{ id: string; tipo_servico: string; raio_operacional_km: number; preco: string | null }>).map((p) => (
                <div key={p.id} className="rounded-lg bg-surface-card p-3 shadow-xs">
                  <p className="text-sm font-semibold">{p.tipo_servico}</p>
                  <p className="text-xs text-neutral-500">Raio {p.raio_operacional_km}km · {p.preco ? formatBRL(p.preco) : 'sob consulta'}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
