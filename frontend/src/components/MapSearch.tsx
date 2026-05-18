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
 */

import L from 'leaflet';
import { useEffect, useMemo } from 'react';
import { Circle, MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';

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
}

function Fit({ markers, userPosition }: { markers: MapMarker[]; userPosition?: LatLng | null }) {
  const map = useMap();
  useEffect(() => {
    if (markers.length) {
      const pts: [number, number][] = markers.map((m) => [m.lat, m.lng]);
      if (userPosition) pts.push([userPosition.lat, userPosition.lng]);
      const bounds = L.latLngBounds(pts);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
      return;
    }
    if (userPosition) {
      map.setView([userPosition.lat, userPosition.lng], 12, { animate: true });
    }
  }, [map, markers, userPosition]);
  return null;
}

export function MapSearch({
  center,
  markers,
  userPosition = null,
  raioKm = null,
  height = '60vh',
  zoom = 12,
}: Props) {
  const c = useMemo(
    () => userPosition ?? center ?? markers[0] ?? BRASIL_CENTRO,
    [userPosition, center, markers],
  );

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

          <Fit markers={markers} userPosition={userPosition} />
        </MapContainer>
      </div>

      {markers.length === 0 && userPosition && (
        <div className="absolute left-1/2 top-3 z-[400] -translate-x-1/2 rounded-full bg-surface-card/95 px-3 py-1.5 text-xs font-semibold text-neutral-700 shadow-sm border border-neutral-200">
          Sem resultados no raio aplicado.
          {raioKm && <span className="ml-1 font-mono text-neutral-500">({raioKm}km)</span>}
        </div>
      )}
    </div>
  );
}
