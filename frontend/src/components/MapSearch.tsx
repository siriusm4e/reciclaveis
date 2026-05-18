/**
 * MapSearch — mapa de busca geolocalizada com pins clicáveis.
 *
 * Pins:
 *   - Verde:   anúncio de venda (também usado p/ localização exata pós-aceite)
 *   - Âmbar:   oferta de compra
 *   - Azul:    "você está aqui" (não confunde com pins de publicação)
 *
 * Cada pin abre um Popup contextual ao clicar — ver MapPinPopup.
 * Quando `userPosition` é fornecido, o mapa abre centrado nele e desenha um
 * círculo do raio configurado para deixar visualmente claro o filtro aplicado.
 *
 * Modo "live map":
 *   - `autoFit={false}` desliga o re-fit automático quando markers mudam (impede
 *     que a busca de re-fetch arraste a câmera do usuário).
 *   - `onSearchInArea` recebe o centro atual ao clicar no botão flutuante
 *     "Buscar nesta área" — botão aparece somente quando o mapa foi panned
 *     além do limiar (~0.001° ≈ ~100m) e some após o callback.
 */

import L from 'leaflet';
import { Search } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Circle,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from 'react-leaflet';

import 'leaflet/dist/leaflet.css';

import { MapPinPopup, type MapPinPopupData } from '@/components/MapPinPopup';
import { BRASIL_CENTRO, type LatLng } from '@/utils/geo';

const ICONS = {
  venda: L.icon({
    iconUrl:
      "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 44' width='32' height='44'%3E%3Cpath fill='%231e8c4e' stroke='%23ffffff' stroke-width='2' d='M16 1c8.3 0 15 6.7 15 15 0 11-15 27-15 27S1 27 1 16C1 7.7 7.7 1 16 1z'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E",
    iconSize: [32, 44],
    iconAnchor: [16, 44],
    popupAnchor: [0, -38],
  }),
  compra: L.icon({
    iconUrl:
      "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 44' width='32' height='44'%3E%3Cpath fill='%23e09c1a' stroke='%23ffffff' stroke-width='2' d='M16 1c8.3 0 15 6.7 15 15 0 11-15 27-15 27S1 27 1 16C1 7.7 7.7 1 16 1z'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E",
    iconSize: [32, 44],
    iconAnchor: [16, 44],
    popupAnchor: [0, -38],
  }),
};

const USER_ICON = L.divIcon({
  className: 'pnr-user-pin',
  html: `
    <div style="position:relative;width:24px;height:24px;">
      <div style="position:absolute;inset:0;border-radius:9999px;background:rgba(37,99,235,0.25);animation:pnrUserPulse 1.6s ease-out infinite;"></div>
      <div style="position:absolute;left:6px;top:6px;width:12px;height:12px;border-radius:9999px;background:#2563eb;border:2px solid #ffffff;box-shadow:0 0 0 1px rgba(0,0,0,0.15);"></div>
    </div>
    <style>@keyframes pnrUserPulse { 0% { transform: scale(0.6); opacity: 0.9; } 100% { transform: scale(2.2); opacity: 0; } }</style>
  `,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const PAN_THRESHOLD_DEG = 0.001; // ~110m em latitude, suficiente para evitar ruído

export interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  tipo: 'venda' | 'compra';
  titulo: string;
  /** Dados adicionais para o Popup contextual. Quando presente, clique abre popup. */
  popup?: Omit<MapPinPopupData, 'publicacao_id' | 'tipo' | 'titulo'>;
  /** Legacy: handler de click custom (sem popup). Não usar junto com popup. */
  onClick?: () => void;
}

interface Props {
  /** Centro inicial (cai em BRASIL_CENTRO se omitido). */
  center?: LatLng;
  markers: MapMarker[];
  /** Posição atual do usuário; quando fornecida, desenha pin azul + círculo de raio. */
  userPosition?: LatLng | null;
  /** Raio (km) do filtro aplicado — usado para desenhar o círculo do usuário. */
  raioKm?: number | null;
  height?: number | string;
  zoom?: number;
  /**
   * Reajustar bounds quando markers/userPosition mudam.
   * - true  (default, retrocompat): re-fitta a câmera a cada change.
   * - false (live map): fita só na primeira renderização válida e respeita pan do usuário.
   */
  autoFit?: boolean;
  /**
   * Quando definido, exibe botão flutuante "Buscar nesta área" no topo do mapa
   * sempre que o usuário panar o mapa além do limiar. Ao clicar, dispara o
   * callback com o centro atual e oculta o botão até o próximo pan.
   */
  onSearchInArea?: (center: LatLng) => void;
  /** Texto do botão flutuante (default "Buscar nesta área"). */
  searchInAreaLabel?: string;
}

/** Recentra programaticamente — usado quando autoFit=true OU na primeira montagem. */
function Fit({
  markers,
  userPosition,
  enabled,
  onPositioned,
}: {
  markers: MapMarker[];
  userPosition?: LatLng | null;
  enabled: boolean;
  onPositioned?: (center: LatLng) => void;
}) {
  const map = useMap();
  useEffect(() => {
    if (!enabled) return;
    if (markers.length) {
      const pts: [number, number][] = markers.map((m) => [m.lat, m.lng]);
      if (userPosition) pts.push([userPosition.lat, userPosition.lng]);
      const bounds = L.latLngBounds(pts);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
      const c = map.getCenter();
      onPositioned?.({ lat: c.lat, lng: c.lng });
      return;
    }
    if (userPosition) {
      map.setView([userPosition.lat, userPosition.lng], 12, { animate: true });
      onPositioned?.(userPosition);
    }
  }, [map, markers, userPosition, enabled, onPositioned]);
  return null;
}

/** Re-centra UMA vez quando userPosition aparece pela primeira vez (modo live). */
function CenterOnceOnUser({
  userPosition,
  onPositioned,
}: {
  userPosition?: LatLng | null;
  onPositioned?: (center: LatLng) => void;
}) {
  const map = useMap();
  const doneRef = useRef(false);
  useEffect(() => {
    if (doneRef.current) return;
    if (!userPosition) return;
    map.setView([userPosition.lat, userPosition.lng], 13, { animate: false });
    doneRef.current = true;
    onPositioned?.(userPosition);
  }, [map, userPosition, onPositioned]);
  return null;
}

/** Detecta pan do usuário e dispara `onPan` com o novo centro. */
function MoveListener({ onPan }: { onPan: (c: LatLng) => void }) {
  useMapEvents({
    moveend: (e) => {
      const c = e.target.getCenter();
      onPan({ lat: c.lat, lng: c.lng });
    },
  });
  return null;
}

export function MapSearch({
  center,
  markers,
  userPosition = null,
  raioKm = null,
  height = '60vh',
  zoom = 12,
  autoFit = true,
  onSearchInArea,
  searchInAreaLabel = 'Buscar nesta área',
}: Props) {
  const c = useMemo(
    () => userPosition ?? center ?? markers[0] ?? BRASIL_CENTRO,
    [userPosition, center, markers],
  );

  // Centro "âncora" — última posição comprometida (busca rodada). Usado pra
  // decidir quando exibir o botão "Buscar nesta área".
  const [anchor, setAnchor] = useState<LatLng>(c);
  const [currentCenter, setCurrentCenter] = useState<LatLng>(c);

  // Sempre que o consumidor fornece um novo userPosition (ou centro inicial muda),
  // re-ancora — evita que o botão fique pendurado depois de uma busca externa.
  useEffect(() => {
    setAnchor(c);
    setCurrentCenter(c);
  }, [c.lat, c.lng]);

  const handlePan = (next: LatLng) => {
    setCurrentCenter(next);
  };

  const handlePositioned = (next: LatLng) => {
    setAnchor(next);
    setCurrentCenter(next);
  };

  const panned =
    Math.abs(currentCenter.lat - anchor.lat) > PAN_THRESHOLD_DEG ||
    Math.abs(currentCenter.lng - anchor.lng) > PAN_THRESHOLD_DEG;

  const shouldShowSearchInArea = Boolean(onSearchInArea) && panned;

  return (
    <div className="relative">
      <div className="overflow-hidden rounded-lg border border-neutral-200" style={{ height }}>
        <MapContainer
          center={[c.lat, c.lng]}
          zoom={zoom}
          scrollWheelZoom
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {userPosition && (
            <>
              <Marker position={[userPosition.lat, userPosition.lng]} icon={USER_ICON} interactive={false} />
              {raioKm && raioKm > 0 && (
                <Circle
                  center={[userPosition.lat, userPosition.lng]}
                  radius={raioKm * 1000}
                  pathOptions={{
                    color: '#2563eb',
                    weight: 1.5,
                    fillColor: '#2563eb',
                    fillOpacity: 0.06,
                    dashArray: '6 4',
                  }}
                />
              )}
            </>
          )}

          {markers.map((m) => {
            const hasPopup = Boolean(m.popup);
            return (
              <Marker
                key={m.id}
                position={[m.lat, m.lng]}
                icon={ICONS[m.tipo]}
                eventHandlers={
                  !hasPopup && m.onClick ? { click: () => m.onClick?.() } : undefined
                }
              >
                {hasPopup && (
                  <Popup minWidth={240} maxWidth={300} closeButton={false} autoPan>
                    <MapPinPopup
                      data={{
                        publicacao_id: m.id,
                        tipo: m.tipo,
                        titulo: m.titulo,
                        ...m.popup!,
                      }}
                    />
                  </Popup>
                )}
              </Marker>
            );
          })}

          {autoFit ? (
            <Fit
              markers={markers}
              userPosition={userPosition}
              enabled
              onPositioned={handlePositioned}
            />
          ) : (
            <CenterOnceOnUser userPosition={userPosition} onPositioned={handlePositioned} />
          )}

          <MoveListener onPan={handlePan} />
        </MapContainer>
      </div>

      {/* Botão flutuante "Buscar nesta área" — só renderiza no modo live map */}
      {shouldShowSearchInArea && (
        <button
          type="button"
          onClick={() => {
            onSearchInArea?.(currentCenter);
            setAnchor(currentCenter);
          }}
          className="absolute left-1/2 top-3 z-[450] -translate-x-1/2 flex items-center gap-1.5 rounded-full border border-neutral-200 bg-surface-card px-4 py-2 text-sm font-semibold text-neutral-900 shadow-md transition-shadow duration-base hover:shadow-lg"
          aria-label={searchInAreaLabel}
        >
          <Search className="h-4 w-4" />
          <span>{searchInAreaLabel}</span>
        </button>
      )}

      {markers.length === 0 && userPosition && !shouldShowSearchInArea && (
        <div className="absolute left-1/2 top-3 z-[400] -translate-x-1/2 rounded-full bg-surface-card/95 px-3 py-1.5 text-xs font-semibold text-neutral-700 shadow-sm border border-neutral-200">
          Sem resultados no raio aplicado.
          {raioKm && <span className="ml-1 font-mono text-neutral-500">({raioKm}km)</span>}
        </div>
      )}
    </div>
  );
}
