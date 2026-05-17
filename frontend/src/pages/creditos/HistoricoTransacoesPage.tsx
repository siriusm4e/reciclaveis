import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { useTransacoesCredito } from '@/hooks/useCreditos';
import { formatDateTime } from '@/utils/dates';
import { formatNumber } from '@/utils/currency';

const TIPO_LABEL: Record<string, string> = {
  compra: 'Compra',
  consumo: 'Consumo',
  reembolso: 'Reembolso',
  ajuste_admin: 'Ajuste',
  bonus: 'Bônus',
};

export default function HistoricoTransacoesPage() {
  const { data, isLoading } = useTransacoesCredito(1);
  return (
    <AppLayout>
      <TopBar title="Histórico de transações" />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState titulo="Sem transações" />
        ) : (
          <ul className="divide-y divide-neutral-100 rounded-lg bg-surface-card border border-neutral-100">
            {data.map((t) => (
              <li key={t.id} className="p-3 flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold">{TIPO_LABEL[t.tipo] ?? t.tipo}</p>
                  <p className="text-xs text-neutral-600">{t.descricao}</p>
                  <p className="text-[10px] text-neutral-400 font-mono">{formatDateTime(t.created_at)}</p>
                </div>
                <p className={`font-mono font-bold ${t.valor >= 0 ? 'text-success-dark' : 'text-error-dark'}`}>
                  {t.valor >= 0 ? '+' : ''}{formatNumber(t.valor)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </AppLayout>
  );
}
