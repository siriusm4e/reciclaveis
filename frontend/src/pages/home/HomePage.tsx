import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { CreditBalance } from '@/components/CreditBalance';
import { GreenHeader } from '@/components/GreenHeader';
import { ListingCard } from '@/components/ListingCard';
import { Button } from '@/components/ui/button';
import { CenterSpinner, EmptyState, ErrorState, SkeletonList } from '@/components/ui/states';
import { useBuscarAnuncios, useBuscarOfertas } from '@/hooks/useAnuncios';
import { useCategorias } from '@/hooks/useCatalogo';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import { useMe } from '@/hooks/useAuth';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import { useMinhasContas } from '@/hooks/useContaAtiva';

export default function HomePage() {
  const navigate = useNavigate();
  const { data: me } = useMe();
  const conta = useContaAtiva();
  const { data: minhasContas, isLoading: loadingContas } = useMinhasContas();
  const { data: categorias } = useCategorias();
  const { obterPosicao, position, loading: loadingGeo } = useGeolocalizacao();
  const [filtroCategoria, setFiltroCategoria] = useState<string | undefined>();

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
      categoria_id: filtroCategoria,
      lat: position?.lat,
      lng: position?.lng,
      raio_km: position ? 50 : undefined,
      page_size: 10,
    }),
    [filtroCategoria, position],
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

      {/* Categorias */}
      <div className="mt-5 px-screen-x">
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-screen-x px-screen-x">
          <button
            type="button"
            onClick={() => setFiltroCategoria(undefined)}
            className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
              !filtroCategoria ? 'bg-primary-500 text-neutral-0' : 'bg-neutral-100 text-neutral-700'
            }`}
          >
            Todas
          </button>
          {categorias?.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => setFiltroCategoria(c.id)}
              className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                filtroCategoria === c.id ? 'bg-primary-500 text-neutral-0' : 'bg-neutral-100 text-neutral-700'
              }`}
            >
              {c.nome}
            </button>
          ))}
        </div>
      </div>

      {/* À venda perto */}
      <section className="mt-5 px-screen-x">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tighter">À venda perto</h2>
          <Button variant="link" size="sm" onClick={() => navigate('/marketplace/buscar')}>
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
              <ListingCard
                key={a.id}
                to={`/anuncios/${a.id}`}
                titulo={a.titulo}
                preco={a.preco_pretendido}
                unidade={a.unidade}
                tipo="venda"
                createdAt={a.created_at}
              />
            ))}
          </div>
        )}
      </section>

      {/* Compradores ativos */}
      <section className="mt-6 px-screen-x">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tighter">Compradores buscando</h2>
          <Button variant="link" size="sm" onClick={() => navigate('/marketplace/buscar?tipo=compra')}>
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
