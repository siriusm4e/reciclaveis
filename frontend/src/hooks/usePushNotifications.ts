/**
 * Push notifications — Capacitor nativo OU Notification API do browser como fallback.
 *
 * O hook é seguro de chamar em qualquer contexto (não bloqueia render).
 * - Em iOS/Android nativo (quando Capacitor estiver presente): registra token FCM/APNs e POSTa em /api/dispositivos/token.
 * - No browser: pede permissão via Notification API e usa um pseudo-token "web:<random>" só para o backend rastrear assinatura.
 * - Em ambientes sem suporte: degrada silenciosamente (toast in-app continua funcionando via notificacoesStore).
 */

import { useCallback, useEffect, useState } from 'react';

import { dispositivosApi } from '@/api/endpoints/conteudo';
import { useAuthStore } from '@/store/authStore';
import { useNotificacoesStore } from '@/store/notificacoesStore';

import { useCapacitor } from './useCapacitor';

type Permission = 'granted' | 'denied' | 'prompt' | 'unsupported';

interface PushApi {
  permission: Permission;
  /** Solicita permissão (browser) ou registra (nativo). */
  requestPermission: () => Promise<Permission>;
  /** Token persistido (FCM/APNs ou pseudo-web). */
  token: string | null;
}

function readBrowserPermission(): Permission {
  if (typeof window === 'undefined' || !('Notification' in window)) return 'unsupported';
  const p = window.Notification.permission;
  if (p === 'granted') return 'granted';
  if (p === 'denied') return 'denied';
  return 'prompt';
}

function generateWebPseudoToken(): string {
  // Token sintético usado SOMENTE como chave para o backend correlacionar.
  // Em produção real o web normalmente NÃO recebe push — a UI usa WebSocket + toast in-app.
  const key = 'pnr.push.web_token';
  const existing = localStorage.getItem(key);
  if (existing) return existing;
  const novo = `web:${crypto.randomUUID()}`;
  localStorage.setItem(key, novo);
  return novo;
}

export function usePushNotifications(): PushApi {
  const { isNative, platform, hasBrowserNotifications } = useCapacitor();
  const isAuthed = useAuthStore((s) => Boolean(s.accessToken));
  const pushToStore = useNotificacoesStore((s) => s.push);

  const [permission, setPermission] = useState<Permission>(() =>
    hasBrowserNotifications ? readBrowserPermission() : 'unsupported',
  );
  const [token, setToken] = useState<string | null>(null);

  // ===== Registro inicial =====
  useEffect(() => {
    if (!isAuthed) return;

    let cancelled = false;
    const run = async () => {
      if (isNative) {
        try {
          // Carrega plugin SOMENTE em runtime nativo para não quebrar build web.
          const mod = await import(
            /* @vite-ignore */ '@capacitor/push-notifications'
          ).catch(() => null);
          if (!mod) return;
          const PushNotifications = mod.PushNotifications;

          const perm = await PushNotifications.requestPermissions();
          if (cancelled) return;
          setPermission(perm.receive === 'granted' ? 'granted' : 'denied');
          if (perm.receive !== 'granted') return;

          await PushNotifications.register();

          PushNotifications.addListener('registration', async (t: { value: string }) => {
            if (cancelled) return;
            setToken(t.value);
            try {
              await dispositivosApi.registrar({
                plataforma: platform === 'web' ? 'web' : platform,
                token: t.value,
              });
            } catch {
              /* o backend pode estar fora — silencioso */
            }
          });

          PushNotifications.addListener('pushNotificationReceived', (notif: { title?: string; body?: string; data?: unknown }) => {
            pushToStore({ titulo: notif.title ?? 'Notificação', corpo: notif.body ?? '', meta: notif.data as Record<string, unknown> });
          });
        } catch {
          /* falha silenciosa — UI continua funcionando */
        }
        return;
      }

      // ===== Browser fallback =====
      if (!hasBrowserNotifications) return;

      const current = readBrowserPermission();
      setPermission(current);
      // Não pede permissão automaticamente — UI dispara via requestPermission().
      const t = generateWebPseudoToken();
      setToken(t);
      try {
        await dispositivosApi.registrar({ plataforma: 'web', token: t });
      } catch {
        /* silencioso */
      }
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [isNative, platform, hasBrowserNotifications, isAuthed, pushToStore]);

  // ===== Solicita permissão sob demanda =====
  const requestPermission = useCallback(async (): Promise<Permission> => {
    if (isNative) {
      const mod = await import(/* @vite-ignore */ '@capacitor/push-notifications').catch(() => null);
      if (!mod) return permission;
      const p = await mod.PushNotifications.requestPermissions();
      const res: Permission = p.receive === 'granted' ? 'granted' : 'denied';
      setPermission(res);
      return res;
    }
    if (!hasBrowserNotifications) return 'unsupported';
    const result = await window.Notification.requestPermission();
    const res: Permission = result === 'granted' ? 'granted' : result === 'denied' ? 'denied' : 'prompt';
    setPermission(res);
    return res;
  }, [isNative, hasBrowserNotifications, permission]);

  return { permission, requestPermission, token };
}
