/**
 * MapPicker — Leaflet com pin ARRASTÁVEL.
 *
 * Funciona puramente no browser (Leaflet + OSM tiles).
 * Usado em criação de Anúncio/Oferta/Pedido para o usuário ajustar o ponto.
 */

import L from 'leaflet';
import { useEffect, useMemo, useState } from 'react';
import { MapContainer, Marker, TileLayer, useMap } from 'react-leaflet';

import 'leaflet/dist/leaflet.css';

import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';

// Garante que os ícones default do Leaflet carreguem (Vite quebra os assets padrão)
const greenIcon = L.icon({
  iconUrl:
    "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 44' width='32' height='44'%3E%3Cpath fill='%231e8c4e' stroke='%23ffffff' stroke-width='2' d='M16 1c8.3 0 15 6.7 15 15 0 11-15 27-15 27S1 27 1 16C1 7.7 7.7 1 16 1z'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E",
  iconSize: [32, 44],
  iconAnchor: [16, 44],
});

function Recenter({ pos }: { pos: LatLng }) {
  const map = useMap();
  useEffect(() => {
    map.setView([pos.lat, pos.lng], map.getZoom(), { animate: true });
  }, [map, pos]);
  return null;
}

interface Props {
  /** Valor controlado (opcional). */
  value?: LatLng;
  defaultValue?: LatLng;
  onChange: (pos: LatLng) => void;
  zoom?: number;
  /** Altura do mapa (default 280px). */
  height?: number | string;
}

export function MapPicker({ value, defaultValue, onChange, zoom = 16, height = 280 }: Props) {
  const initial = useMemo<LatLng>(
    () => value ?? defaultValue ?? SAO_PAULO_CAPITAL,
    [value, defaultValue],
  );
  const [pos, setPos] = useState<LatLng>(initial);

  useEffect(() => {
    if (value && (value.lat !== pos.lat || value.lng !== pos.lng)) {
      setPos(value);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value?.lat, value?.lng]);

  return (
    <div className="overflow-hidden rounded-lg border border-neutral-200" style={{ height }}>
      <MapContainer
        center={[pos.lat, pos.lng]}
        zoom={zoom}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker
          position={[pos.lat, pos.lng]}
          draggable
          icon={greenIcon}
          eventHandlers={{
            dragend: (e) => {
              const m = e.target as L.Marker;
              const ll = m.getLatLng();
              const next = { lat: ll.lat, lng: ll.lng };
              setPos(next);
              onChange(next);
            },
          }}
        />
        <Recenter pos={pos} />
      </MapContainer>
    </div>
  );
}
