import { useQuery } from '@tanstack/react-query';
import { ShoppingCart, Tag } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { anunciosVendaApi, ofertasCompraApi } from '@/api/endpoints/marketplace';
import { AppLayout } from '@/components/AppLayout';
import { CreditBalance } from '@/components/CreditBalance';
import { GreenHeader } from '@/components/GreenHeader';
import { MapSearch, type MapMarker } from '@/components/MapSearch';
import { CenterSpinner } from '@/components/ui/states';
import { useMe } from '@/hooks/useAuth';
import { useContaAtiva, useMinhasContas, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import type { AnuncioVenda, OfertaCompra, PapelTipo } from '@/types/api';
import { type LatLng } from '@/utils/geo';

// Fallback quando a geolocalização falha — Curitiba, capital do PR (POC do cliente).
const CURITIBA: LatLng = { lat: -25.4284, lng: -49.2733 };

type ModoMapa = 'compradores' | 'vendedores' | 'ambos';

const PAPEIS_VENDEDOR: PapelTipo[] = ['catador', 'coletor', 'acumulador', 'gerador_industrial'];
const PAPEIS_COMPRADOR: PapelTipo[] = ['comprador', 'gestor_residuos', 'revendedor_equipamentos'];

function getModoInicial(papeisAtivos: PapelTipo[]): ModoMapa {
  const temVendedor = papeisAtivos.some((p) => PAPEIS_VENDEDOR.includes(p));
  const temComprador = papeisAtivos.some((p) => PAPEIS_COMPRADOR.includes(p));
  if (temVendedor && !temComprador) return 'compradores'; // catador vê quem compra
  if (temComprador && !temVendedor) return 'vendedores'; // comprador vê quem vende
  return 'ambos';
}

function getRaioInicial(papeisAtivos: PapelTipo[]): number {
  if (papeisAtivos.includes('catador')) return 2;
  if (papeisAtivos.includes('coletor')) return 5;
  if (papeisAtivos.includes('acumulador')) return 15;
  if (papeisAtivos.includes('comprador')) return 25;
  if (papeisAtivos.includes('gerador_industrial')) return 50;
  return 10;
}

export default function HomePage() {
  const navigate = useNavigate();
  const { data: me } = useMe();
  const conta = useContaAtiva();
  const { data: minhasContas, isLoading: loadingContas } = useMinhasContas();
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const { obterPosicao, position, loading: loadingGeo, error: geoError } = useGeolocalizacao();

  // Auto-pede geolocalização ao entrar (uma vez)
  useEffect(() => {
    if (!position) void obterPosicao();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Redireciona usuário sem Conta para onboarding — exceto usuários do
  // backoffice (perfil interno), que operam sem Conta e vão para /admin.
  useEffect(() => {
    if (me?.perfil_interno) {
      navigate('/admin');
      return;
    }
    if (!loadingContas && minhasContas && minhasContas.length === 0) {
      navigate('/onboarding');
    }
  }, [me, loadingContas, minhasContas, navigate]);

  // Papéis ativos da conta atual (lista pode estar vazia)
  const papeisAtivos: PapelTipo[] = useMemo(
    () => (papeis ?? []).filter((p) => p.status === 'ativo').map((p) => p.papel),
    [papeis],
  );

  // Modo e raio iniciais derivados do papel principal — recalculam quando papéis carregam
  const modoInicial = useMemo(() => getModoInicial(papeisAtivos), [papeisAtivos]);
  const raioInicial = useMemo(() => getRaioInicial(papeisAtivos), [papeisAtivos]);

  const [modo, setModo] = useState<ModoMapa>('ambos');
  const [raio, setRaio] = useState<number>(10);
  // sincroniza apenas quando os defaults derivados mudam — usuário ainda pode trocar
  const [modoUserOverride, setModoUserOverride] = useState(false);
  useEffect(() => {
    if (!modoUserOverride) setModo(modoInicial);
    setRaio(raioInicial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modoInicial, raioInicial]);

  // Centro de busca — começa em position OU Curitiba (fallback). "Buscar nesta área" atualiza.
  const [centroBusca, setCentroBusca] = useState<LatLng | null>(null);
  useEffect(() => {
    if (position && !centroBusca) setCentroBusca(position);
    if (!position && geoError && !centroBusca) setCentroBusca(CURITIBA);
  }, [position, geoError, centroBusca]);

  const lat = centroBusca?.lat;
  const lng = centroBusca?.lng;

  const buscarVendedores = modo !== 'compradores';
  const buscarCompradores = modo !== 'vendedores';

  const anunciosQ = useQuery({
    queryKey: ['home-mapa-anuncios', lat, lng, raio],
    queryFn: () =>
      anunciosVendaApi.buscar({ lat: lat!, lng: lng!, raio_km: raio, page_size: 100 }),
    enabled: !!lat && !!lng && buscarVendedores,
    staleTime: 60_000,
  });

  const ofertasQ = useQuery({
    queryKey: ['home-mapa-ofertas', lat, lng, raio],
    queryFn: () =>
      ofertasCompraApi.buscar({ lat: lat!, lng: lng!, raio_km: raio, page_size: 100 }),
    enabled: !!lat && !!lng && buscarCompradores,
    staleTime: 60_000,
  });

  // Markers — combina anúncios (verde) + ofertas (âmbar) conforme o modo ativo
  const markers: MapMarker[] = useMemo(() => {
    const out: MapMarker[] = [];
    if (buscarVendedores && anunciosQ.data) {
      for (const a of anunciosQ.data as AnuncioVenda[]) {
        out.push({
          id: a.id,
          lat: a.lat_pub,
          lng: a.lng_pub,
          tipo: 'venda',
          titulo: 'Material à venda',
          popup: {
            preco: a.preco_pretendido,
            unidade: a.unidade,
            conta_id: a.conta_id,
            volume: a.volume_estimado,
          },
        });
      }
    }
    if (buscarCompradores && ofertasQ.data) {
      for (const o of ofertasQ.data as OfertaCompra[]) {
        out.push({
          id: o.id,
          lat: o.lat,
          lng: o.lng,
          tipo: 'compra',
          titulo: o.titulo,
          popup: {
            preco: o.preco_paga,
            unidade: o.unidade,
            conta_id: o.conta_id,
            descricao: o.descricao,
            volume: o.volume_min,
            boost_ativo: o.boost_ativo,
            raio_km: o.raio_km,
            retira: o.retira,
          },
        });
      }
    }
    return out;
  }, [anunciosQ.data, ofertasQ.data, buscarVendedores, buscarCompradores]);

  if (loadingContas) {
    return (
      <AppLayout>
        <CenterSpinner />
      </AppLayout>
    );
  }

  const saudacao = me ? `Olá, ${me.nome_completo.split(' ')[0]}!` : 'Bem-vindo';
  const localLabel = loadingGeo
    ? 'Buscando local...'
    : position
      ? `Raio ${raio}km`
      : 'Ativar localização';

  const setModoUI = (m: ModoMapa) => {
    setModo(m);
    setModoUserOverride(true);
  };

  const onSearchInArea = (c: LatLng) => {
    setCentroBusca(c);
  };

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

      {/* === Ações principais — Comprar / Vender abrem em LISTA === */}
      <section className="mt-5 px-screen-x">
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => navigate('/marketplace/buscar?modo=comprar&view=lista')}
            className="flex min-h-[52px] items-center justify-center gap-2 rounded-xl bg-primary-500 px-4 py-3 text-base font-bold uppercase tracking-wide text-neutral-0 shadow-sm transition-shadow duration-base hover:shadow-md"
            aria-label="Comprar — buscar anúncios de venda em lista"
          >
            <ShoppingCart className="h-5 w-5" />
            <span>Comprar</span>
          </button>
          <button
            type="button"
            onClick={() => navigate('/marketplace/buscar?modo=vender&view=lista')}
            className="flex min-h-[52px] items-center justify-center gap-2 rounded-xl bg-accent-500 px-4 py-3 text-base font-bold uppercase tracking-wide text-neutral-900 shadow-sm transition-shadow duration-base hover:shadow-md"
            aria-label="Vender — buscar compradores em lista"
          >
            <Tag className="h-5 w-5" />
            <span>Vender</span>
          </button>
        </div>
      </section>

      {/* === Toggle de modo do mapa === */}
      <section className="mt-4 px-screen-x">
        <div className="flex gap-2" role="tablist" aria-label="Tipo de pin exibido no mapa">
          <button
            type="button"
            role="tab"
            aria-selected={modo === 'compradores'}
            onClick={() => setModoUI('compradores')}
            className={`flex-1 rounded-full px-4 py-1.5 text-sm font-medium transition-colors duration-base ${
              modo === 'compradores'
                ? 'bg-accent-500 text-neutral-900'
                : modo === 'ambos'
                  ? 'border border-accent-300 bg-surface-card text-accent-600'
                  : 'bg-neutral-100 text-neutral-600'
            }`}
          >
            Compradores
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={modo === 'vendedores'}
            onClick={() => setModoUI('vendedores')}
            className={`flex-1 rounded-full px-4 py-1.5 text-sm font-medium transition-colors duration-base ${
              modo === 'vendedores'
                ? 'bg-primary-500 text-neutral-0'
                : modo === 'ambos'
                  ? 'border border-primary-300 bg-surface-card text-primary-700'
                  : 'bg-neutral-100 text-neutral-600'
            }`}
          >
            Vendedores
          </button>
          {modo !== 'ambos' && (
            <button
              type="button"
              onClick={() => {
                setModoUI('ambos');
              }}
              className="rounded-full bg-neutral-100 px-3 py-1.5 text-xs font-medium text-neutral-600"
              aria-label="Ver ambos"
            >
              Ambos
            </button>
          )}
        </div>
      </section>

      {/* === Mapa === */}
      <section className="mt-3 px-screen-x">
        {!position && loadingGeo && (
          <div
            className="flex items-center justify-center rounded-lg border border-neutral-200 bg-neutral-100 text-sm text-neutral-600"
            style={{ height: 360 }}
          >
            Obtendo sua localização...
          </div>
        )}

        {centroBusca && (
          <>
            {!position && (
              <div className="mb-2 rounded-lg bg-warning-light px-3 py-2 text-xs text-warning-dark">
                Ative a localização para ver resultados mais próximos —
                <button
                  type="button"
                  onClick={() => void obterPosicao()}
                  className="ml-1 font-semibold underline"
                >
                  tentar agora
                </button>
              </div>
            )}
            <MapSearch
              center={centroBusca}
              userPosition={position}
              raioKm={raio}
              markers={markers}
              height={360}
              zoom={13}
              autoFit={false}
              onSearchInArea={onSearchInArea}
            />
            {markers.length === 0 && !anunciosQ.isLoading && !ofertasQ.isLoading && (
              <p className="mt-2 text-center text-xs text-neutral-500">
                Nenhum resultado em {raio}km. Tente aumentar o raio na busca.
              </p>
            )}
          </>
        )}
      </section>
    </AppLayout>
  );
}
