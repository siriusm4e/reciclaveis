/** Helpers de coordenadas para o mapa Leaflet. */

export interface LatLng {
  lat: number;
  lng: number;
}

export const SAO_PAULO_CAPITAL: LatLng = { lat: -23.5505, lng: -46.6333 };
export const BRASIL_CENTRO: LatLng = { lat: -14.235, lng: -51.9253 };

export function formatCoord(value: number): string {
  return value.toFixed(6);
}

export function haversineKm(a: LatLng, b: LatLng): number {
  const R = 6371;
  const φ1 = (a.lat * Math.PI) / 180;
  const φ2 = (b.lat * Math.PI) / 180;
  const dφ = ((b.lat - a.lat) * Math.PI) / 180;
  const dλ = ((b.lng - a.lng) * Math.PI) / 180;
  const x =
    Math.sin(dφ / 2) ** 2 +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(dλ / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
}
