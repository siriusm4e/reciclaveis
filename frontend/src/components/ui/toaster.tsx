import { useEffect, useState } from 'react';

import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from './toast';

type Variant = 'default' | 'success' | 'warning' | 'error' | 'info';

interface ToastItem {
  id: string;
  title: string;
  description?: string;
  variant?: Variant;
  duration?: number;
}

type ToastEvent = CustomEvent<Omit<ToastItem, 'id'>>;

const EVENT = 'pnr.toast';

export function showToast(opts: Omit<ToastItem, 'id'>) {
  window.dispatchEvent(new CustomEvent(EVENT, { detail: opts }) as ToastEvent);
}

export function Toaster() {
  const [items, setItems] = useState<ToastItem[]>([]);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as ToastEvent).detail;
      const id = crypto.randomUUID();
      setItems((s) => [...s, { id, ...detail }]);
      setTimeout(() => setItems((s) => s.filter((i) => i.id !== id)), detail.duration ?? 5000);
    };
    window.addEventListener(EVENT, handler as EventListener);
    return () => window.removeEventListener(EVENT, handler as EventListener);
  }, []);

  return (
    <ToastProvider>
      {items.map((it) => (
        <Toast key={it.id} variant={it.variant} duration={it.duration ?? 5000}>
          <div className="flex-1">
            <ToastTitle>{it.title}</ToastTitle>
            {it.description && <ToastDescription>{it.description}</ToastDescription>}
          </div>
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport />
    </ToastProvider>
  );
}
