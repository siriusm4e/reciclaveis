import { Coins } from 'lucide-react';
import { Link } from 'react-router-dom';

import { useSaldoCreditos } from '@/hooks/useCreditos';
import { cn } from '@/lib/utils';
import { formatNumber } from '@/utils/currency';

export function CreditBalance({ inline = false }: { inline?: boolean }) {
  const { data, isLoading } = useSaldoCreditos();
  const valor = data?.saldo ?? 0;

  return (
    <Link
      to="/creditos"
      className={cn(
        'inline-flex items-center gap-2 rounded-full bg-accent-500/15 px-3 py-1.5 text-accent-600 transition-colors hover:bg-accent-500/25',
        inline ? 'text-sm' : 'text-base',
      )}
    >
      <Coins className="h-4 w-4" />
      <span className="font-mono font-bold tabular-nums">
        {isLoading ? '...' : formatNumber(valor)}
      </span>
      <span className="text-xs uppercase tracking-wider opacity-80">Créditos</span>
    </Link>
  );
}
