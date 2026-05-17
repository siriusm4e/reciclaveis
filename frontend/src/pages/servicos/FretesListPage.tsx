import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { ListingCard } from '@/components/ListingCard';
import { TopBar } from '@/components/TopBar';
import { EmptyState, SkeletonList } from '@/components/ui/states';
import { useBuscarFretes } from '@/hooks/useAnuncios';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';

export default function FretesListPage() {
  const navigate = useNavigate();
  const { position } = useGeolocalizacao();
  const { data, isLoading } = useBuscarFretes({
    lat: position?.lat,
    lng: position?.lng,
    raio_km: position ? 500 : undefined,
  });

  return (
    <AppLayout>
      <TopBar title="Fretes" />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <SkeletonList rows={3} />
        ) : !data?.length ? (
          <EmptyState
            titulo="Sem fretes disponíveis"
            acao={{ label: 'Publicar frete', onClick: () => navigate('/fretes/criar') }}
          />
        ) : (
          <div className="space-y-3">
            {data.map((f) => (
              <ListingCard
                key={f.id}
                to={`/fretes/criar`} // sem detalhe dedicado no MVP, listing já mostra essencial
                titulo={`${f.tipo_veiculo} · ${f.raio_operacional_km}km`}
                preco={f.capacidade_t ? `${f.capacidade_t}t` : null}
                tipo="frete"
                createdAt={f.created_at}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
