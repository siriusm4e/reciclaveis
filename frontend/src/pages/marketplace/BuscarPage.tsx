import { MapPin, Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { ConditionSelector } from '@/components/ConditionSelector';
import { ListingCard } from '@/components/ListingCard';
import { MapSearch } from '@/components/MapSearch';
import { TopBar } from '@/components/TopBar';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { EmptyState, ErrorState, SkeletonList } from '@/components/ui/states';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useBuscarAnuncios, useBuscarOfertas } from '@/hooks/useAnuncios';
import { useCategorias, useSubcategorias, useTiposMaterial } from '@/hooks/useCatalogo';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import type { CondicaoForma, CondicaoLimpeza, CondicaoUmidade } from '@/types/api';
import { type LatLng } from '@/utils/geo';

// Faixas pré-definidas de volume (em kg)
const VOLUME_BANDS = [
  { value: 'any', label: 'Qualquer volume', min: undefined as number | undefined },
  { value: 'ate100', label: 'Até 100 kg', min: 0 },
  { value: '100a1k', label: '100 kg – 1 t', min: 100 },
  { value: '1ka5k', label: '1 – 5 t', min: 1000 },
  { value: 'acima5k', label: 'Acima de 5 t', min: 5000 },
];

type ColetaFilter = 'todas' | 'retira' | 'entrega' | 'precisa_frete';

interface NominatimResult {
  lat: string;
  lon: string;
  display_name: string;
}

async function geocodificarEndereco(
  query: string,
): Promise<{ lat: number; lng: number; nome: string } | null> {
  const q = query.trim();
  if (q.length < 3) return null;
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&countrycodes=br&limit=1&accept-language=pt-BR`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Geocoding ${res.status}`);
  const data = (await res.json()) as NominatimResult[];
  if (!data.length) return null;
  return {
    lat: Number.parseFloat(data[0].lat),
    lng: Number.parseFloat(data[0].lon),
    nome: data[0].display_name,
  };
}

export default function MarketplaceBuscarPage() {
  const [params] = useSearchParams();
  const initialTipo: 'venda' | 'compra' =
    params.get('modo') === 'vender' || params.get('tipo') === 'compra' ? 'compra' : 'venda';

  // ?view=lista vem dos botões Comprar/Vender da Home; default = mapa
  const initialView: 'mapa' | 'lista' = params.get('view') === 'lista' ? 'lista' : 'mapa';
  const [view, setView] = useState<'mapa' | 'lista'>(initialView);
  const [tipo, setTipo] = useState<'venda' | 'compra'>(initialTipo);

  // Cascata de filtros: Categoria → Subcategoria → Tipo
  const [categoriaId, setCategoriaId] = useState<string | undefined>();
  const [subcategoriaId, setSubcategoriaId] = useState<string | undefined>();
  const [tipoMaterialId, setTipoMaterialId] = useState<string | undefined>();

  const { data: categorias } = useCategorias();
  const { data: subcategorias } = useSubcategorias(categoriaId ?? null);
  const { data: tipos } = useTiposMaterial(subcategoriaId ?? null);

  // Reseta dependentes quando o pai muda
  useEffect(() => {
    setSubcategoriaId(undefined);
    setTipoMaterialId(undefined);
  }, [categoriaId]);
  useEffect(() => {
    setTipoMaterialId(undefined);
  }, [subcategoriaId]);

  // Slider de raio (1-500km, default 25)
  const [raio, setRaio] = useState(25);

  // Filtros de condição (grupos exclusivos)
  const [condLimpeza, setCondLimpeza] = useState<CondicaoLimpeza | null>(null);
  const [condUmidade, setCondUmidade] = useState<CondicaoUmidade | null>(null);
  const [condForma, setCondForma] = useState<CondicaoForma | null>(null);

  // Filtro de volume (banda)
  const [volumeBand, setVolumeBand] = useState<string>('any');
  const volumeMin = VOLUME_BANDS.find((b) => b.value === volumeBand)?.min;

  // Filtro de coleta (só faz sentido em busca de ofertas — comprador retira ou não)
  const [coleta, setColeta] = useState<ColetaFilter>('todas');

  const { position, obterPosicao } = useGeolocalizacao();

  // === Busca por endereço (Nominatim) — controla centro independente da geo ===
  const [endereco, setEndereco] = useState('');
  const [enderecoLabel, setEnderecoLabel] = useState<string | null>(null);
  const [geocodLoading, setGeocodLoading] = useState(false);
  const [geocodError, setGeocodError] = useState<string | null>(null);
  // Centro de busca efetivo. Prioridade:
  //   1. último endereço geocodificado / "Buscar nesta área"
  //   2. geolocalização do usuário
  const [centroSelecionado, setCentroSelecionado] = useState<LatLng | null>(null);
  const centroEfetivo: LatLng | null = centroSelecionado ?? position ?? null;

  const buscaParams = useMemo(
    () => ({
      categoria_id: categoriaId,
      subcategoria_id: subcategoriaId,
      tipo_material_id: tipoMaterialId,
      lat: centroEfetivo?.lat,
      lng: centroEfetivo?.lng,
      raio_km: centroEfetivo ? raio : undefined,
      condicao_limpeza: condLimpeza ?? undefined,
      condicao_umidade: condUmidade ?? undefined,
      condicao_forma: condForma ?? undefined,
      // Volume: venda → volume_minimo_kg (comprador querendo no mínimo X)
      //         compra → volume_disponivel_kg (vendedor declara que tem X)
      volume_minimo_kg: tipo === 'venda' ? volumeMin : undefined,
      volume_disponivel_kg: tipo === 'compra' ? volumeMin : undefined,
      page_size: 50,
    }),
    [
      categoriaId,
      subcategoriaId,
      tipoMaterialId,
      centroEfetivo,
      raio,
      condLimpeza,
      condUmidade,
      condForma,
      volumeMin,
      tipo,
    ],
  );

  const anuncios = useBuscarAnuncios(tipo === 'venda' ? buscaParams : {});
  const ofertas = useBuscarOfertas(tipo === 'compra' ? buscaParams : {});

  let items = tipo === 'venda' ? anuncios.data ?? [] : ofertas.data ?? [];

  // Filtro de coleta (aplicado client-side em ofertas)
  if (tipo === 'compra' && coleta !== 'todas') {
    items = (items as any[]).filter((it) => {
      if (coleta === 'retira') return it.retira === true;
      if (coleta === 'entrega') return it.retira === false;
      // precisa_frete: não retira E não tem MTR/licença (proxy: assume sempre verdade)
      if (coleta === 'precisa_frete') return it.retira === false;
      return true;
    });
  }

  // Helper para exibir nome do tipo de material (lookup pelo cache local)
  const nomeDoTipo = (id?: string) => tipos?.find((t) => t.id === id)?.nome ?? null;

  const onBuscarEndereco = async () => {
    if (!endereco.trim()) return;
    setGeocodLoading(true);
    setGeocodError(null);
    try {
      const result = await geocodificarEndereco(endereco);
      if (!result) {
        setGeocodError('Endereço não encontrado');
        setEnderecoLabel(null);
        return;
      }
      setCentroSelecionado({ lat: result.lat, lng: result.lng });
      setEnderecoLabel(result.nome);
    } catch {
      setGeocodError('Falha ao buscar endereço. Verifique sua conexão.');
    } finally {
      setGeocodLoading(false);
    }
  };

  const onUsarMinhaLocalizacao = async () => {
    const pos = await obterPosicao();
    setCentroSelecionado(null); // limpa override de endereço — efetivo volta a ser `position`
    setEnderecoLabel(null);
    setGeocodError(null);
    // pos já caiu em `position` via useGeolocalizacao; centroEfetivo recalcula
    void pos;
  };

  const onSearchInArea = (c: LatLng) => {
    setCentroSelecionado(c);
    setEnderecoLabel(null);
  };

  return (
    <AppLayout>
      <TopBar title="Buscar" />
      <div className="px-screen-x py-4 space-y-3">
        {/* Tabs: Vender (à venda) / Comprar (compradores) */}
        <Tabs value={tipo} onValueChange={(v) => setTipo(v as 'venda' | 'compra')}>
          <TabsList className="w-full">
            <TabsTrigger value="venda" className="flex-1">À venda</TabsTrigger>
            <TabsTrigger value="compra" className="flex-1">Compradores</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* === Busca por endereço (Nominatim) — só faz sentido no modo mapa === */}
        {view === 'mapa' && (
          <div>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
                <Input
                  value={endereco}
                  onChange={(e) => setEndereco(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      void onBuscarEndereco();
                    }
                  }}
                  placeholder="Digite endereço ou cidade..."
                  className="pl-9"
                  aria-label="Buscar endereço ou cidade"
                />
              </div>
              <button
                type="button"
                onClick={() => void onBuscarEndereco()}
                disabled={geocodLoading || !endereco.trim()}
                className="inline-flex min-h-[44px] min-w-[80px] items-center justify-center gap-1 rounded-md bg-primary-500 px-3 text-sm font-semibold text-neutral-0 shadow-sm disabled:opacity-50"
              >
                <Search className="h-4 w-4" />
                {geocodLoading ? '...' : 'Buscar'}
              </button>
              <button
                type="button"
                onClick={() => void onUsarMinhaLocalizacao()}
                className="inline-flex min-h-[44px] items-center justify-center gap-1 rounded-md border border-neutral-200 bg-surface-card px-3 text-sm font-medium text-neutral-700"
                aria-label="Usar minha localização"
              >
                <MapPin className="h-4 w-4" />
              </button>
            </div>
            {enderecoLabel && (
              <p className="mt-1 text-xs text-neutral-600 truncate">{enderecoLabel}</p>
            )}
            {geocodError && (
              <p className="mt-1 text-xs font-medium text-[#dc2626]">{geocodError}</p>
            )}
          </div>
        )}

        {/* === Dropdowns encadeados Categoria → Subcategoria → Tipo === */}
        <div className="grid grid-cols-3 gap-2">
          <Select value={categoriaId ?? 'todas'} onValueChange={(v) => setCategoriaId(v === 'todas' ? undefined : v)}>
            <SelectTrigger><SelectValue placeholder="Categoria" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="todas">Categoria</SelectItem>
              {categorias?.map((c) => (
                <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={subcategoriaId ?? 'todas'}
            onValueChange={(v) => setSubcategoriaId(v === 'todas' ? undefined : v)}
            disabled={!categoriaId}
          >
            <SelectTrigger><SelectValue placeholder="Subcategoria" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="todas">Subcategoria</SelectItem>
              {subcategorias?.map((s) => (
                <SelectItem key={s.id} value={s.id}>{s.nome}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={tipoMaterialId ?? 'todas'}
            onValueChange={(v) => setTipoMaterialId(v === 'todas' ? undefined : v)}
            disabled={!subcategoriaId}
          >
            <SelectTrigger><SelectValue placeholder="Tipo" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="todas">Tipo</SelectItem>
              {tipos?.map((t) => (
                <SelectItem key={t.id} value={t.id}>{t.nome}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* === Filtros adicionais === */}
        <details className="rounded-lg border border-neutral-200 bg-surface-card">
          <summary className="cursor-pointer px-3 py-2 text-sm font-semibold text-neutral-700">
            Filtros avançados
          </summary>
          <div className="px-3 pb-3 space-y-3 pt-1">
            {/* Raio (slider 1-500) */}
            <div>
              <div className="flex items-baseline justify-between">
                <Label>Raio</Label>
                <span className="font-mono text-sm font-semibold text-primary-700">{raio} km</span>
              </div>
              <input
                type="range"
                min={1}
                max={500}
                step={1}
                value={raio}
                onChange={(e) => setRaio(Number(e.target.value))}
                className="w-full accent-primary-500"
                aria-label="Raio em km, mínimo 1, máximo 500"
              />
              <div className="flex justify-between text-[10px] text-neutral-500">
                <span>1 km</span>
                <span>500 km</span>
              </div>
              {!position && !centroSelecionado && (
                <button
                  type="button"
                  onClick={() => void obterPosicao()}
                  className="mt-1 w-full rounded-md bg-primary-50 p-2 text-xs text-primary-700"
                >
                  Usar minha localização
                </button>
              )}
            </div>

            {/* Volume (faixas) */}
            <div>
              <Label>Volume</Label>
              <Select value={volumeBand} onValueChange={setVolumeBand}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {VOLUME_BANDS.map((b) => (
                    <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Coleta (só faz sentido em compra) */}
            {tipo === 'compra' && (
              <div>
                <Label>Coleta</Label>
                <Select value={coleta} onValueChange={(v) => setColeta(v as ColetaFilter)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todas">Todas</SelectItem>
                    <SelectItem value="retira">Retira no local</SelectItem>
                    <SelectItem value="entrega">Entrega (vendedor leva)</SelectItem>
                    <SelectItem value="precisa_frete">Precisa de frete</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Condição (3 grupos exclusivos) */}
            <ConditionSelector group="limpeza" value={condLimpeza} onChange={setCondLimpeza} />
            <ConditionSelector group="umidade" value={condUmidade} onChange={setCondUmidade} />
            <ConditionSelector group="forma" value={condForma} onChange={setCondForma} />
          </div>
        </details>

        {/* === Toggle Mapa / Lista (default vem da URL ?view=) === */}
        <Tabs value={view} onValueChange={(v) => setView(v as 'mapa' | 'lista')}>
          <TabsList>
            <TabsTrigger value="mapa">Mapa</TabsTrigger>
            <TabsTrigger value="lista">Lista</TabsTrigger>
          </TabsList>

          <TabsContent value="mapa">
            <MapSearch
              center={centroEfetivo ?? undefined}
              userPosition={position ?? undefined}
              raioKm={centroEfetivo ? raio : null}
              autoFit={false}
              onSearchInArea={onSearchInArea}
              markers={(items as any[]).map((it) => ({
                id: it.id,
                lat: tipo === 'venda' ? it.lat_pub : it.lat,
                lng: tipo === 'venda' ? it.lng_pub : it.lng,
                tipo,
                titulo: tipo === 'venda'
                  ? nomeDoTipo(it.tipo_material_id) ?? 'Material à venda'
                  : it.titulo,
                popup: {
                  preco: tipo === 'venda' ? it.preco_pretendido : it.preco_paga,
                  unidade: it.unidade,
                  conta_id: it.conta_id,
                  descricao: tipo === 'venda' ? null : it.descricao,
                  volume: tipo === 'venda' ? it.volume_estimado : it.volume_min,
                  boost_ativo: tipo === 'compra' ? it.boost_ativo : undefined,
                  raio_km: tipo === 'compra' ? it.raio_km : undefined,
                  retira: tipo === 'compra' ? it.retira : undefined,
                },
              }))}
              height="60vh"
            />
            {tipo === 'venda' && (
              <p className="mt-2 text-[10px] text-neutral-500 px-1">
                Localizações exibidas no mapa são aproximadas (privacidade do vendedor).
              </p>
            )}
          </TabsContent>

          <TabsContent value="lista">
            {(tipo === 'venda' ? anuncios.isLoading : ofertas.isLoading) ? (
              <SkeletonList rows={4} />
            ) : (tipo === 'venda' ? anuncios.error : ofertas.error) ? (
              <ErrorState onRetry={() => (tipo === 'venda' ? anuncios.refetch() : ofertas.refetch())} />
            ) : items.length === 0 ? (
              <EmptyState titulo="Nada por aqui ainda" descricao="Tente trocar a categoria, ampliar o raio ou desabilitar o filtro de localização." />
            ) : (
              <div className="space-y-3">
                {(items as any[]).map((it) => (
                  <ListingCard
                    key={it.id}
                    to={tipo === 'venda' ? `/anuncios/${it.id}` : `/ofertas/${it.id}`}
                    titulo={
                      tipo === 'venda'
                        ? nomeDoTipo(it.tipo_material_id) ?? 'Material à venda'
                        : it.titulo
                    }
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
        </Tabs>
      </div>
    </AppLayout>
  );
}
