import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { ListingCard } from '@/components/ListingCard';
import { TopBar } from '@/components/TopBar';
import { EmptyState, ErrorState, SkeletonList } from '@/components/ui/states';
import { useBuscarMaquinas } from '@/hooks/useAnuncios';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';

export default function MaquinasListPage() {
  const navigate = useNavigate();
  const { position } = useGeolocalizacao();
  const { data, isLoading, error, refetch } = useBuscarMaquinas({
    lat: position?.lat,
    lng: position?.lng,
    raio_km: position ? 200 : undefined,
  });

  return (
    <AppLayout>
      <TopBar title="Equipamentos" />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <SkeletonList rows={3} />
        ) : error ? (
          <ErrorState onRetry={refetch} />
        ) : !data?.length ? (
          <EmptyState
            titulo="Nenhum equipamento"
            descricao="Anuncie ou aguarde novas publicações de máquinas."
            acao={{ label: 'Publicar', onClick: () => navigate('/maquinas/criar') }}
          />
        ) : (
          <div className="space-y-3">
            {data.map((m) => (
              <ListingCard
                key={m.id}
                to={`/maquinas/${m.id}`}
                titulo={`${m.marca ?? ''} ${m.modelo ?? m.categoria_equipamento}`}
                preco={m.preco}
                tipo="maquina"
                createdAt={m.created_at}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
