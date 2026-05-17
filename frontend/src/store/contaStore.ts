import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { Conta, ID, Papel } from '@/types/api';

interface ContaState {
  contaAtivaId: ID | null;
  contaAtiva: Conta | null;
  papelAtivoId: ID | null;
  setContaAtiva: (c: Conta | null) => void;
  setPapelAtivo: (p: Papel | null) => void;
  clear: () => void;
}

export const useContaStore = create<ContaState>()(
  persist(
    (set) => ({
      contaAtivaId: null,
      contaAtiva: null,
      papelAtivoId: null,
      setContaAtiva: (c) =>
        set({ contaAtiva: c, contaAtivaId: c?.id ?? null, papelAtivoId: null }),
      setPapelAtivo: (p) => set({ papelAtivoId: p?.id ?? null }),
      clear: () => set({ contaAtiva: null, contaAtivaId: null, papelAtivoId: null }),
    }),
    {
      name: 'pnr.conta',
      partialize: (s) => ({
        contaAtivaId: s.contaAtivaId,
        contaAtiva: s.contaAtiva,
        papelAtivoId: s.papelAtivoId,
      }),
    },
  ),
);
