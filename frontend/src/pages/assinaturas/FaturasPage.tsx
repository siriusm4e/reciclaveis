import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useFaturas, usePagarFatura } from '@/hooks/useCreditos';
import { centsToBRL } from '@/utils/currency';
import { formatDate } from '@/utils/dates';

export default function FaturasPage() {
  const { data, isLoading } = useFaturas();
  const pagar = usePagarFatura();

  return (
    <AppLayout>
      <TopBar title="Faturas" />
      <div className="px-screen-x py-4 space-y-3">
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState titulo="Sem faturas" />
        ) : (
          data.map((f) => (
            <Card key={f.id} className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wider text-neutral-500">
                    Ciclo {formatDate(f.ciclo_inicio)} → {formatDate(f.ciclo_fim)}
                  </p>
                  <p className="mt-1 font-mono text-xl font-bold">{centsToBRL(f.valor_centavos)}</p>
                  <p className="text-xs text-neutral-500">Vence em <span className="font-mono">{formatDate(f.vencimento)}</span></p>
                </div>
                <StatusBadge status={f.status} />
              </div>
              {f.status === 'pendente' && (
                <Button
                  size="sm"
                  className="mt-2"
                  onClick={() =>
                    pagar.mutate(
                      { id: f.id },
                      {
                        onSuccess: () => showToast({ title: 'Pagamento processado', variant: 'success' }),
                        onError: (err) =>
                          showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
                      },
                    )
                  }
                  loading={pagar.isPending}
                >
                  Pagar agora
                </Button>
              )}
            </Card>
          ))
        )}
      </div>
    </AppLayout>
  );
}
