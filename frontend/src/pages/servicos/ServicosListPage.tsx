import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { ListingCard } from '@/components/ListingCard';
import { TopBar } from '@/components/TopBar';
import { EmptyState, SkeletonList } from '@/components/ui/states';
import { useBuscarServicos } from '@/hooks/useAnuncios';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';

export default function ServicosListPage() {
  const navigate = useNavigate();
  const { position } = useGeolocalizacao();
  const { data, isLoading } = useBuscarServicos({
    lat: position?.lat,
    lng: position?.lng,
    raio_km: position ? 200 : undefined,
  });

  return (
    <AppLayout>
      <TopBar title="Serviços" />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <SkeletonList rows={3} />
        ) : !data?.length ? (
          <EmptyState
            titulo="Sem serviços ativos"
            acao={{ label: 'Publicar serviço', onClick: () => navigate('/servicos/criar') }}
          />
        ) : (
          <div className="space-y-3">
            {data.map((s) => (
              <ListingCard
                key={s.id}
                to={`/servicos/${s.id}`}
                titulo={s.tipo_servico}
                preco={s.preco}
                unidade={s.unidade_cobranca}
                tipo="servico"
                createdAt={s.created_at}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
