/**
 * useNotificacoes — assina o WebSocket `/ws/notificacoes` por Conta ativa
 * e popula notificacoesStore com toasts/badges in-app.
 *
 * Funciona puramente no browser via WebSocket nativo. Sem dependência de Capacitor.
 */

import { useEffect } from 'react';

import { useAuthStore } from '@/store/authStore';
import { useContaStore } from '@/store/contaStore';
import { useNotificacoesStore } from '@/store/notificacoesStore';

function buildWsUrl(token: string, contaId: string): string {
  const base = import.meta.env.VITE_WS_URL || '/ws';
  let url: string;
  if (/^wss?:/.test(base)) {
    url = base;
  } else {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    url = `${proto}//${window.location.host}${base.startsWith('/') ? base : `/${base}`}`;
  }
  const sep = url.includes('?') ? '&' : '?';
  return `${url.replace(/\/$/, '')}/notificacoes${sep}token=${encodeURIComponent(token)}&conta_id=${encodeURIComponent(contaId)}`;
}

export function useNotificacoesRealtime(): void {
  const token = useAuthStore((s) => s.accessToken);
  const contaId = useContaStore((s) => s.contaAtivaId);
  const pushNotif = useNotificacoesStore((s) => s.push);

  useEffect(() => {
    if (!token || !contaId) return;
    let ws: WebSocket | null = null;
    let pingTimer: ReturnType<typeof setInterval> | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let cancelled = false;

    const connect = () => {
      try {
        ws = new WebSocket(buildWsUrl(token, contaId));
      } catch {
        return;
      }
      ws.onopen = () => {
        pingTimer = setInterval(() => ws?.readyState === WebSocket.OPEN && ws.send('ping'), 30_000);
      };
      ws.onmessage = (evt) => {
        if (typeof evt.data !== 'string' || evt.data === 'pong') return;
        try {
          const parsed = JSON.parse(evt.data) as {
            evento?: string;
            payload?: { titulo?: string; corpo?: string; [k: string]: unknown };
          };
          if (parsed?.payload?.titulo || parsed?.payload?.corpo) {
            pushNotif({
              titulo: parsed.payload.titulo ?? 'Notificação',
              corpo: parsed.payload.corpo ?? '',
              meta: parsed.payload,
            });
          }
        } catch {
          /* ignora binário/json inválido */
        }
      };
      ws.onclose = () => {
        if (pingTimer) clearInterval(pingTimer);
        if (cancelled) return;
        reconnectTimer = setTimeout(connect, 4000);
      };
      ws.onerror = () => ws?.close();
    };

    connect();
    return () => {
      cancelled = true;
      if (pingTimer) clearInterval(pingTimer);
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [token, contaId, pushNotif]);
}

/** Hook do chat de uma Negociação — assina ws/negociacao/{id} e dispara callback por mensagem. */
export function useChatRealtime(negociacaoId: string | null, onMessage: (e: { evento: string; payload: Record<string, unknown> }) => void): void {
  const token = useAuthStore((s) => s.accessToken);
  const contaId = useContaStore((s) => s.contaAtivaId);

  useEffect(() => {
    if (!token || !contaId || !negociacaoId) return;
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let cancelled = false;

    const buildUrl = () => {
      const base = import.meta.env.VITE_WS_URL || '/ws';
      let url: string;
      if (/^wss?:/.test(base)) {
        url = base;
      } else {
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        url = `${proto}//${window.location.host}${base.startsWith('/') ? base : `/${base}`}`;
      }
      return `${url.replace(/\/$/, '')}/negociacao/${negociacaoId}?token=${encodeURIComponent(token)}&conta_id=${encodeURIComponent(contaId)}`;
    };

    const connect = () => {
      try {
        ws = new WebSocket(buildUrl());
      } catch {
        return;
      }
      ws.onmessage = (evt) => {
        try {
          const parsed = JSON.parse(evt.data);
          onMessage(parsed);
        } catch {
          /* ignora */
        }
      };
      ws.onclose = () => {
        if (cancelled) return;
        reconnectTimer = setTimeout(connect, 4000);
      };
      ws.onerror = () => ws?.close();
    };

    connect();
    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [token, contaId, negociacaoId, onMessage]);
}
