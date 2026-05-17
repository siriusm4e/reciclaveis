import { type ReactNode } from 'react';
import { cn } from '@/lib/utils';

/**
 * Frame mobile-first — em desktop centraliza num "celular" de 390px.
 * No mobile/PWA/Capacitor ocupa toda a tela com safe-area.
 */
export function MobileFrame({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className="min-h-screen w-full bg-neutral-900 md:py-6 flex justify-center">
      <div
        className={cn(
          'relative w-full md:max-w-phone bg-surface-background md:rounded-3xl md:shadow-xl overflow-hidden',
          'shell-mobile',
          className,
        )}
      >
        {children}
      </div>
    </div>
  );
}
