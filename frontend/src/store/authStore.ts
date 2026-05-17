import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { TokenPair, UsuarioPublic } from '@/types/api';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: number | null;
  usuario: UsuarioPublic | null;
  mfaRequired: boolean;

  setTokens: (tokens: TokenPair) => void;
  setUsuario: (u: UsuarioPublic | null) => void;
  setMfaRequired: (v: boolean) => void;
  clear: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
      usuario: null,
      mfaRequired: false,

      setTokens: (tokens) =>
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          expiresAt: Date.now() + tokens.expires_in * 1000,
          mfaRequired: false,
        }),

      setUsuario: (u) => set({ usuario: u }),
      setMfaRequired: (v) => set({ mfaRequired: v }),

      clear: () =>
        set({
          accessToken: null,
          refreshToken: null,
          expiresAt: null,
          usuario: null,
          mfaRequired: false,
        }),

      isAuthenticated: () => {
        const { accessToken, expiresAt } = get();
        return Boolean(accessToken && expiresAt && expiresAt > Date.now());
      },
    }),
    {
      name: 'pnr.auth',
      partialize: (s) => ({
        accessToken: s.accessToken,
        refreshToken: s.refreshToken,
        expiresAt: s.expiresAt,
        usuario: s.usuario,
      }),
    },
  ),
);
