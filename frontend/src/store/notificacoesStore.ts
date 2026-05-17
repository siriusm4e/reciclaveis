import { create } from 'zustand';

export interface NotificacaoInApp {
  id: string;
  titulo: string;
  corpo: string;
  ts: number;
  lida: boolean;
  meta?: Record<string, unknown>;
}

interface NotifState {
  itens: NotificacaoInApp[];
  push: (n: Omit<NotificacaoInApp, 'id' | 'ts' | 'lida'>) => void;
  marcarLida: (id: string) => void;
  marcarTodasLidas: () => void;
  remover: (id: string) => void;
  limpar: () => void;
  naoLidas: () => number;
}

export const useNotificacoesStore = create<NotifState>()((set, get) => ({
  itens: [],
  push: (n) =>
    set((s) => ({
      itens: [
        {
          id: crypto.randomUUID(),
          ts: Date.now(),
          lida: false,
          ...n,
        },
        ...s.itens,
      ].slice(0, 100),
    })),
  marcarLida: (id) =>
    set((s) => ({ itens: s.itens.map((i) => (i.id === id ? { ...i, lida: true } : i)) })),
  marcarTodasLidas: () => set((s) => ({ itens: s.itens.map((i) => ({ ...i, lida: true })) })),
  remover: (id) => set((s) => ({ itens: s.itens.filter((i) => i.id !== id) })),
  limpar: () => set({ itens: [] }),
  naoLidas: () => get().itens.filter((i) => !i.lida).length,
}));
