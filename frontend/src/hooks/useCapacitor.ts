/**
 * Detecção de runtime Capacitor com FALLBACK total para browser.
 *
 * O app inteiro funciona no browser sem Capacitor. Este hook apenas informa
 * em que contexto estamos rodando para que componentes possam adaptar:
 * ex.: usar safe-area maior em iOS nativo, ou esconder algum botão.
 *
 * Nunca BLOQUEIE telas em isNative=false — o web é o caminho primário.
 */

import { useMemo } from 'react';

interface CapacitorRuntime {
  /** True só quando rodando empacotado pelo Capacitor (iOS/Android nativo). */
  isNative: boolean;
  /** 'ios' | 'android' | 'web' */
  platform: 'ios' | 'android' | 'web';
  /** True se o navegador suporta as principais Web APIs que usamos como fallback. */
  hasBrowserGeolocation: boolean;
  hasBrowserNotifications: boolean;
}

function detect(): CapacitorRuntime {
  // window.Capacitor existe quando o bundle roda dentro do wrapper nativo.
  // Em browser puro fica `undefined` e tudo cai em fallback.
  const cap = (typeof window !== 'undefined' && (window as unknown as { Capacitor?: unknown }).Capacitor) as
    | { isNativePlatform?: () => boolean; getPlatform?: () => string }
    | undefined;

  let isNative = false;
  let platform: 'ios' | 'android' | 'web' = 'web';

  if (cap && typeof cap.isNativePlatform === 'function') {
    try {
      isNative = cap.isNativePlatform();
      const p = cap.getPlatform?.() ?? 'web';
      platform = p === 'ios' || p === 'android' ? p : 'web';
    } catch {
      isNative = false;
      platform = 'web';
    }
  }

  return {
    isNative,
    platform,
    hasBrowserGeolocation:
      typeof navigator !== 'undefined' && typeof navigator.geolocation !== 'undefined',
    hasBrowserNotifications:
      typeof window !== 'undefined' && typeof window.Notification !== 'undefined',
  };
}

export function useCapacitor(): CapacitorRuntime {
  return useMemo(detect, []);
}

/** Helper síncrono para código fora de componentes (ex.: stores). */
export function isCapacitorNative(): boolean {
  return detect().isNative;
}
