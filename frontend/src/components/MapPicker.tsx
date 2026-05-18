/**
 * MapPicker — Leaflet com pin ARRASTÁVEL + busca de endereço (Nominatim/OSM).
 *
 * Funciona puramente no browser. Geocoding via Nominatim público
 * (https://nominatim.openstreetmap.org) — sem chave, com limite ~1 req/s.
 *
 * Para desabilitar a busca, passe `showAddressSearch={false}`.
 */

import L from 'leaflet';
import { Loader2, MapPin, Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { MapContainer, Marker, TileLayer, useMap } from 'react-leaflet';

import 'leaflet/dist/leaflet.css';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';

// Pin verde inline (sem dependência de assets externos)
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
  /** Mostrar campo de busca de endereço acima do mapa (default true). */
  showAddressSearch?: boolean;
  /** Label do campo de endereço. */
  addressLabel?: string;
}

interface NominatimResult {
  lat: string;
  lon: string;
  display_name: string;
}

async function geocode(address: string): Promise<{ pos: LatLng; label: string } | null> {
  const q = address.trim();
  if (q.length < 3) return null;
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&countrycodes=br&limit=1&accept-language=pt-BR`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Geocoding ${res.status}`);
  const data = (await res.json()) as NominatimResult[];
  if (!data.length) return null;
  return {
    pos: { lat: Number.parseFloat(data[0].lat), lng: Number.parseFloat(data[0].lon) },
    label: data[0].display_name,
  };
}

export function MapPicker({
  value,
  defaultValue,
  onChange,
  zoom = 16,
  height = 280,
  showAddressSearch = true,
  addressLabel = 'Buscar endereço (rua, número, cidade)',
}: Props) {
  const initial = useMemo<LatLng>(
    () => value ?? defaultValue ?? SAO_PAULO_CAPITAL,
    [value, defaultValue],
  );
  const [pos, setPos] = useState<LatLng>(initial);
  const [address, setAddress] = useState('');
  const [searching, setSearching] = useState(false);
  const [resolvedLabel, setResolvedLabel] = useState<string | null>(null);

  useEffect(() => {
    if (value && (value.lat !== pos.lat || value.lng !== pos.lng)) {
      setPos(value);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value?.lat, value?.lng]);

  const handleSearch = async () => {
    if (!address.trim()) return;
    setSearching(true);
    try {
      const result = await geocode(address);
      if (!result) {
        showToast({
          title: 'Endereço não encontrado',
          description: 'Tente acrescentar cidade e estado.',
          variant: 'warning',
        });
        return;
      }
      setPos(result.pos);
      setResolvedLabel(result.label);
      onChange(result.pos);
    } catch {
      showToast({
        title: 'Falha ao buscar endereço',
        description: 'Verifique sua conexão e tente novamente.',
        variant: 'error',
      });
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-2">
      {showAddressSearch && (
        <div>
          <Label htmlFor="map-address">{addressLabel}</Label>
          <div className="flex gap-2">
            <Input
              id="map-address"
              type="search"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  void handleSearch();
                }
              }}
              placeholder="Ex.: Av. Paulista 1000, São Paulo SP"
              className="flex-1"
            />
            <Button
              type="button"
              variant="secondary"
              size="default"
              onClick={() => void handleSearch()}
              disabled={!address.trim() || searching}
              aria-label="Buscar endereço"
            >
              {searching ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>
          {resolvedLabel && (
            <p className="mt-1 flex items-start gap-1 text-[10px] text-neutral-500">
              <MapPin className="h-3 w-3 mt-0.5 shrink-0" />
              <span className="line-clamp-2">{resolvedLabel}</span>
            </p>
          )}
          <p className="text-[10px] text-neutral-400 mt-1">
            Você ainda pode <strong>arrastar o pin</strong> para ajustar a localização exata.
          </p>
        </div>
      )}

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
    </div>
  );
}
