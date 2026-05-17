import { useParams } from 'react-router-dom';

import { servicosApi } from '@/api/endpoints/marketplace';
import { useQuery } from '@tanstack/react-query';

import { AppLayout } from '@/components/AppLayout';
import { MapSearch } from '@/components/MapSearch';
import { TopBar } from '@/components/TopBar';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { formatBRL } from '@/utils/currency';

export default function ServicoDetalhePage() {
  const { id = '' } = useParams();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['anuncios-servico', id],
    queryFn: () => servicosApi.get(id),
    enabled: !!id,
  });

  if (isLoading) return <AppLayout><CenterSpinner /></AppLayout>;
  if (error || !data) return <AppLayout><ErrorState onRetry={refetch} /></AppLayout>;

  return (
    <AppLayout>
      <TopBar title={data.tipo_servico} />
      <div className="px-screen-x py-4 space-y-4">
        <h1 className="text-2xl font-bold tracking-tighter">{data.tipo_servico}</h1>
        <p className="font-mono text-2xl font-bold text-primary-700">
          {data.preco ? formatBRL(data.preco) : 'Sob consulta'}
          <span className="ml-1 text-sm font-normal text-neutral-600">/{data.unidade_cobranca}</span>
        </p>
        <p className="text-sm">Raio operacional: <span className="font-mono">{data.raio_operacional_km}km</span></p>
        {data.descricao && <p className="font-serif italic text-neutral-700">{data.descricao}</p>}
        <MapSearch
          center={{ lat: data.lat, lng: data.lng }}
          markers={[{ id: data.id, lat: data.lat, lng: data.lng, tipo: 'venda', titulo: data.tipo_servico }]}
          height={200}
        />
      </div>
    </AppLayout>
  );
}
