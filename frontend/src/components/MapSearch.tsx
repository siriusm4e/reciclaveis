/**
 * MapSearch — mapa de busca geolocalizada com pins.
 *
 * Verde: anúncio de venda. Âmbar: oferta de compra. Pin verde também é usado
 * para localização EXATA pós-aceite (privacy by design: cor não revela diferença).
 */

import L from 'leaflet';
import { useEffect, useMemo } from 'react';
import { MapContainer, Marker, TileLayer, useMap } from 'react-leaflet';

import 'leaflet/dist/leaflet.css';

import { BRASIL_CENTRO, type LatLng } from '@/utils/geo';

const ICONS = {
  venda: L.icon({
    iconUrl:
      "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 44' width='32' height='44'%3E%3Cpath fill='%231e8c4e' stroke='%23ffffff' stroke-width='2' d='M16 1c8.3 0 15 6.7 15 15 0 11-15 27-15 27S1 27 1 16C1 7.7 7.7 1 16 1z'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E",
    iconSize: [32, 44],
    iconAnchor: [16, 44],
  }),
  compra: L.icon({
    iconUrl:
      "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 44' width='32' height='44'%3E%3Cpath fill='%23e09c1a' stroke='%23ffffff' stroke-width='2' d='M16 1c8.3 0 15 6.7 15 15 0 11-15 27-15 27S1 27 1 16C1 7.7 7.7 1 16 1z'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E",
    iconSize: [32, 44],
    iconAnchor: [16, 44],
  }),
};

export interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  tipo: 'venda' | 'compra';
  titulo: string;
  preco?: string | number | null;
  onClick?: () => void;
}

interface Props {
  center?: LatLng;
  markers: MapMarker[];
  height?: number | string;
  zoom?: number;
}

function Fit({ markers }: { markers: MapMarker[] }) {
  const map = useMap();
  useEffect(() => {
    if (!markers.length) return;
    const bounds = L.latLngBounds(markers.map((m) => [m.lat, m.lng]));
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
  }, [map, markers]);
  return null;
}

export function MapSearch({ center, markers, height = '60vh', zoom = 12 }: Props) {
  const c = useMemo(() => center ?? markers[0] ?? BRASIL_CENTRO, [center, markers]);

  return (
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
        {markers.map((m) => (
          <Marker
            key={m.id}
            position={[m.lat, m.lng]}
            icon={ICONS[m.tipo]}
            eventHandlers={m.onClick ? { click: () => m.onClick?.() } : undefined}
          />
        ))}
        <Fit markers={markers} />
      </MapContainer>
    </div>
  );
}
