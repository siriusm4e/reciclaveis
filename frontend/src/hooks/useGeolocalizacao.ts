/**
 * Geolocalização — Capacitor nativo OU navigator.geolocation como fallback.
 *
 * Funciona no browser SEM dependência de Capacitor. UI nunca bloqueia.
 */

import { useCallback, useState } from 'react';

import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';

import { useCapacitor } from './useCapacitor';

interface GeoApi {
  loading: boolean;
  error: string | null;
  /** Última posição lida (ou null se ainda não solicitou). */
  position: LatLng | null;
  /** Solicita a posição atual. Resolve sempre — em caso de erro, devolve SP capital. */
  obterPosicao: () => Promise<LatLng>;
}

function readBrowserPosition(): Promise<LatLng> {
  return new Promise((resolve, reject) => {
    if (typeof navigator === 'undefined' || !navigator.geolocation) {
      reject(new Error('Geolocalização indisponível neste navegador'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude }),
      (err) => reject(err),
      { enableHighAccuracy: true, timeout: 10_000, maximumAge: 60_000 },
    );
  });
}

export function useGeolocalizacao(): GeoApi {
  const { isNative, hasBrowserGeolocation } = useCapacitor();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [position, setPosition] = useState<LatLng | null>(null);

  const obterPosicao = useCallback(async (): Promise<LatLng> => {
    setLoading(true);
    setError(null);
    try {
      if (isNative) {
        const mod = await import(
          /* @vite-ignore */ '@capacitor/geolocation'
        ).catch(() => null);
        if (mod) {
          const perm = await mod.Geolocation.requestPermissions();
          if (perm.location === 'granted') {
            const r = await mod.Geolocation.getCurrentPosition({
              enableHighAccuracy: true,
              timeout: 10_000,
            });
            const pos: LatLng = { lat: r.coords.latitude, lng: r.coords.longitude };
            setPosition(pos);
            return pos;
          }
          throw new Error('Permissão de localização negada');
        }
        // se plugin falhar em runtime nativo, cai pra browser API
      }
      if (hasBrowserGeolocation) {
        const pos = await readBrowserPosition();
        setPosition(pos);
        return pos;
      }
      throw new Error('Geolocalização indisponível');
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao obter localização';
      setError(msg);
      // Fallback final: SP capital — UI não trava.
      setPosition(SAO_PAULO_CAPITAL);
      return SAO_PAULO_CAPITAL;
    } finally {
      setLoading(false);
    }
  }, [isNative, hasBrowserGeolocation]);

  return { loading, error, position, obterPosicao };
}
