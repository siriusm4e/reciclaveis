import { ShoppingCart, Tag } from 'lucide-react';
import { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { CreditBalance } from '@/components/CreditBalance';
import { GreenHeader } from '@/components/GreenHeader';
import { ListingCard } from '@/components/ListingCard';
import { Button } from '@/components/ui/button';
import { CenterSpinner, EmptyState, ErrorState, SkeletonList } from '@/components/ui/states';
import { useBuscarAnuncios, useBuscarOfertas } from '@/hooks/useAnuncios';
import { useTipoMaterial } from '@/hooks/useCatalogo';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import { useMe } from '@/hooks/useAuth';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { useMinhasContas } from '@/hooks/useContaAtiva';
import type { AnuncioVenda } from '@/types/api';

// Card de AnuncioVenda — resolve nome do TipoMaterial via cache do React Query.
// Anúncios do mesmo tipo compartilham a query (staleTime 5min), evitando N+1 real.
function AnuncioVendaCard({ a }: { a: AnuncioVenda }) {
  const { data: tipo } = useTipoMaterial(a.tipo_material_id);
  return (
    <ListingCard
      to={`/anuncios/${a.id}`}
      titulo={tipo?.nome ?? 'Material à venda'}
      preco={a.preco_pretendido}
      unidade={a.unidade}
      tipo="venda"
      createdAt={a.created_at}
    />
  );
}

export default function HomePage() {
  const navigate = useNavigate();
  const { data: me } = useMe();
  const conta = useContaAtiva();
  const { data: minhasContas, isLoading: loadingContas } = useMinhasContas();
  const { obterPosicao, position, loading: loadingGeo } = useGeolocalizacao();

  // Auto-pede geolocalização ao entrar
  useEffect(() => {
    if (!position) void obterPosicao();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Redireciona usuário sem Conta para onboarding
  useEffect(() => {
    if (!loadingContas && minhasContas && minhasContas.length === 0) {
      navigate('/onboarding');
    }
  }, [loadingContas, minhasContas, navigate]);

  const buscaParams = useMemo(
    () => ({
      lat: position?.lat,
      lng: position?.lng,
      raio_km: position ? 50 : undefined,
      page_size: 10,
    }),
    [position],
  );

  const anuncios = useBuscarAnuncios(buscaParams);
  const ofertas = useBuscarOfertas(buscaParams);

  if (loadingContas) {
    return (
      <AppLayout>
        <CenterSpinner />
      </AppLayout>
    );
  }

  const saudacao = me ? `Olá, ${me.nome_completo.split(' ')[0]}!` : 'Bem-vindo';
  const localLabel = loadingGeo ? 'Buscando local...' : position ? `Raio 50km` : 'Selecionar local';

  return (
    <AppLayout>
      <GreenHeader
        saudacao={saudacao}
        localizacaoLabel={localLabel}
        onClickLocalizacao={() => void obterPosicao()}
      />

      <div className="px-screen-x mt-3 flex items-center justify-between gap-2">
        <CreditBalance inline />
        <span className="text-xs text-neutral-500 truncate max-w-[160px] text-right">
          {conta?.nome_publico ?? '—'}
        </span>
      </div>

      {/* === Ações principais — Comprar / Vender ===
          COMPRAR  → busca anúncios de venda  (sou potencial comprador)
          VENDER   → busca ofertas de compra (sou potencial vendedor, busco compradores)
          Ambas levam para o BuscarPage, que abre no mapa por padrão. */}
      <section className="mt-5 px-screen-x">
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => navigate('/marketplace/buscar?modo=comprar')}
            className="flex min-h-[52px] items-center justify-center gap-2 rounded-xl bg-primary-500 px-4 py-3 text-base font-bold uppercase tracking-wide text-neutral-0 shadow-sm transition-shadow duration-base hover:shadow-md"
            aria-label="Comprar — buscar anúncios de venda no mapa"
          >
            <ShoppingCart className="h-5 w-5" />
            <span>Comprar</span>
          </button>
          <button
            type="button"
            onClick={() => navigate('/marketplace/buscar?modo=vender')}
            className="flex min-h-[52px] items-center justify-center gap-2 rounded-xl bg-accent-500 px-4 py-3 text-base font-bold uppercase tracking-wide text-neutral-900 shadow-sm transition-shadow duration-base hover:shadow-md"
            aria-label="Vender — buscar compradores no mapa"
          >
            <Tag className="h-5 w-5" />
            <span>Vender</span>
          </button>
        </div>
      </section>

      {/* À venda perto */}
      <section className="mt-6 px-screen-x">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tighter">À venda perto</h2>
          <Button variant="link" size="sm" onClick={() => navigate('/marketplace/buscar?modo=comprar')}>
            Ver tudo
          </Button>
        </div>
        {anuncios.isLoading ? (
          <SkeletonList rows={3} />
        ) : anuncios.error ? (
          <ErrorState onRetry={() => anuncios.refetch()} />
        ) : !anuncios.data?.length ? (
          <EmptyState titulo="Nenhum anúncio na sua região" descricao="Tente ampliar o raio ou trocar a categoria." />
        ) : (
          <div className="space-y-3">
            {anuncios.data.slice(0, 5).map((a) => (
              <AnuncioVendaCard key={a.id} a={a} />
            ))}
          </div>
        )}
      </section>

      {/* Compradores ativos */}
      <section className="mt-6 px-screen-x">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tighter">Compradores buscando</h2>
          <Button variant="link" size="sm" onClick={() => navigate('/marketplace/buscar?modo=vender')}>
            Ver tudo
          </Button>
        </div>
        {ofertas.isLoading ? (
          <SkeletonList rows={2} />
        ) : !ofertas.data?.length ? (
          <p className="text-sm text-neutral-500">Sem demandas ativas na sua região.</p>
        ) : (
          <div className="space-y-3">
            {ofertas.data.slice(0, 4).map((o) => (
              <ListingCard
                key={o.id}
                to={`/ofertas/${o.id}`}
                titulo={o.titulo}
                preco={o.preco_paga}
                unidade={o.unidade}
                tipo="compra"
                createdAt={o.created_at}
                destaque={o.boost_ativo}
              />
            ))}
          </div>
        )}
      </section>
    </AppLayout>
  );
}
