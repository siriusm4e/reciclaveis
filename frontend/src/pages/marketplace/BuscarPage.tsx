import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { ListingCard } from '@/components/ListingCard';
import { MapSearch } from '@/components/MapSearch';
import { TopBar } from '@/components/TopBar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { EmptyState, ErrorState, SkeletonList } from '@/components/ui/states';
import { useBuscarAnuncios, useBuscarOfertas } from '@/hooks/useAnuncios';
import { useCategorias } from '@/hooks/useCatalogo';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';

export default function MarketplaceBuscarPage() {
  const [params] = useSearchParams();
  const [view, setView] = useState<'lista' | 'mapa'>('lista');
  const [tipo, setTipo] = useState<'venda' | 'compra'>(params.get('tipo') === 'compra' ? 'compra' : 'venda');
  const [categoriaId, setCategoriaId] = useState<string | undefined>();
  const [raio, setRaio] = useState(50);
  const { data: categorias } = useCategorias();
  const { position, obterPosicao } = useGeolocalizacao();

  const buscaParams = useMemo(
    () => ({
      categoria_id: categoriaId,
      lat: position?.lat,
      lng: position?.lng,
      raio_km: position ? raio : undefined,
      page_size: 50,
    }),
    [categoriaId, position, raio],
  );

  const anuncios = useBuscarAnuncios(tipo === 'venda' ? buscaParams : {});
  const ofertas = useBuscarOfertas(tipo === 'compra' ? buscaParams : {});

  const items = tipo === 'venda' ? anuncios.data ?? [] : ofertas.data ?? [];

  return (
    <AppLayout>
      <TopBar title="Buscar" />
      <div className="px-screen-x py-4 space-y-3">
        <Tabs value={tipo} onValueChange={(v) => setTipo(v as 'venda' | 'compra')}>
          <TabsList className="w-full">
            <TabsTrigger value="venda" className="flex-1">
              À venda
            </TabsTrigger>
            <TabsTrigger value="compra" className="flex-1">
              Compradores
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="flex gap-2">
          <div className="flex-1">
            <Select value={categoriaId ?? 'todas'} onValueChange={(v) => setCategoriaId(v === 'todas' ? undefined : v)}>
              <SelectTrigger><SelectValue placeholder="Categoria" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as categorias</SelectItem>
                {categorias?.map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="w-28">
            <Select value={String(raio)} onValueChange={(v) => setRaio(Number(v))}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {[10, 25, 50, 100, 250].map((r) => (
                  <SelectItem key={r} value={String(r)}>{r} km</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {!position && (
          <button
            type="button"
            onClick={() => void obterPosicao()}
            className="w-full rounded-lg bg-primary-50 p-2 text-sm text-primary-700"
          >
            Usar minha localização
          </button>
        )}

        <Tabs value={view} onValueChange={(v) => setView(v as 'lista' | 'mapa')}>
          <TabsList>
            <TabsTrigger value="lista">Lista</TabsTrigger>
            <TabsTrigger value="mapa">Mapa</TabsTrigger>
          </TabsList>

          <TabsContent value="lista">
            {(tipo === 'venda' ? anuncios.isLoading : ofertas.isLoading) ? (
              <SkeletonList rows={4} />
            ) : (tipo === 'venda' ? anuncios.error : ofertas.error) ? (
              <ErrorState onRetry={() => (tipo === 'venda' ? anuncios.refetch() : ofertas.refetch())} />
            ) : items.length === 0 ? (
              <EmptyState titulo="Nada por aqui ainda" descricao="Tente trocar a categoria, ampliar o raio ou desabilitar o filtro de localização." />
            ) : (
              <div className="space-y-3">
                {items.map((it: any) => (
                  <ListingCard
                    key={it.id}
                    to={tipo === 'venda' ? `/anuncios/${it.id}` : `/ofertas/${it.id}`}
                    titulo={it.titulo}
                    preco={tipo === 'venda' ? it.preco_pretendido : it.preco_paga}
                    unidade={it.unidade}
                    tipo={tipo}
                    createdAt={it.created_at}
                    destaque={tipo === 'compra' && it.boost_ativo}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="mapa">
            <MapSearch
              center={position ?? undefined}
              markers={items.map((it: any) => ({
                id: it.id,
                lat: tipo === 'venda' ? it.lat_pub : it.lat,
                lng: tipo === 'venda' ? it.lng_pub : it.lng,
                tipo,
                titulo: it.titulo,
                preco: tipo === 'venda' ? it.preco_pretendido : it.preco_paga,
              }))}
              height="60vh"
            />
            {tipo === 'venda' && (
              <p className="mt-2 text-[10px] text-neutral-500 px-1">
                Localizações exibidas no mapa são aproximadas (privacidade do vendedor).
              </p>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}
