import { History, ShoppingBag } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useSaldoCreditos } from '@/hooks/useCreditos';
import { formatNumber } from '@/utils/currency';

export default function CreditosPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useSaldoCreditos();

  return (
    <AppLayout>
      <TopBar title="Créditos" />
      <div className="px-screen-x py-4 space-y-4">
        <Card className="p-5 bg-gradient-to-br from-accent-500/10 to-accent-500/5 border-accent-500/30">
          <p className="text-xs uppercase tracking-wider text-accent-600">Saldo disponível</p>
          <p className="font-mono text-5xl font-bold text-accent-600">
            {isLoading ? '...' : formatNumber(data?.saldo ?? 0)}
          </p>
          <p className="text-xs text-neutral-500 mt-1">Saldo é projeção do ledger (não há expiração no MVP).</p>
        </Card>

        <Button variant="accent" className="w-full" onClick={() => navigate('/creditos/comprar')}>
          <ShoppingBag className="h-4 w-4" /> Comprar Créditos
        </Button>

        <Link
          to="/creditos/historico"
          className="flex items-center justify-between rounded-lg bg-surface-card border border-neutral-100 p-3 text-sm"
        >
          <span className="inline-flex items-center gap-2">
            <History className="h-4 w-4 text-primary-600" /> Histórico de transações
          </span>
          <span className="text-neutral-400">›</span>
        </Link>
      </div>
    </AppLayout>
  );
}
