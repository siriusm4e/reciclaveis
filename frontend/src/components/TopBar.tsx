import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { cn } from '@/lib/utils';

interface Props {
  title: string;
  action?: React.ReactNode;
  back?: boolean;
  variant?: 'light' | 'dark';
}

export function TopBar({ title, action, back = true, variant = 'light' }: Props) {
  const navigate = useNavigate();
  const dark = variant === 'dark';
  return (
    <header
      className={cn(
        'sticky top-0 z-topbar flex h-topbar items-center gap-2 px-2 pt-safe',
        dark ? 'bg-surface-dark text-neutral-0' : 'bg-surface-card text-neutral-900 border-b border-neutral-100',
      )}
    >
      {back && (
        <button
          type="button"
          onClick={() => navigate(-1)}
          className={cn(
            'flex h-10 w-10 items-center justify-center rounded-full transition-colors',
            dark ? 'hover:bg-white/15' : 'hover:bg-neutral-100',
          )}
          aria-label="Voltar"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
      )}
      <h1 className="flex-1 truncate text-lg font-bold tracking-tighter">{title}</h1>
      {action}
    </header>
  );
}
