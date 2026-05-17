import { Link, useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import {
  useCancelarAssinatura,
  useMinhasAssinaturas,
} from '@/hooks/useCreditos';
import { formatDate } from '@/utils/dates';

export default function PlanoAtualPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useMinhasAssinaturas();
  const cancelar = useCancelarAssinatura();

  return (
    <AppLayout>
      <TopBar title="Plano e Assinaturas" />
      <div className="px-screen-x py-4 space-y-3">
        <Button onClick={() => navigate('/assinaturas/upgrade')} className="w-full">
          Comparar planos
        </Button>
        <Link to="/faturas" className="block text-sm text-primary-700 underline">
          Ver faturas
        </Link>

        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState titulo="Sem assinaturas ativas" descricao="Cada Papel da Conta pode ter um Plano próprio." />
        ) : (
          data.map((a) => (
            <Card key={a.id} className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wider text-neutral-500">Papel ID</p>
                  <p className="font-mono text-xs">{a.papel_id.slice(0, 8)}...</p>
                  <p className="mt-1 text-xs">Renova em <span className="font-mono">{formatDate(a.data_renovacao)}</span></p>
                </div>
                <StatusBadge status={a.status} />
              </div>
              {a.status !== 'cancelada' && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="mt-2 text-error"
                  onClick={() =>
                    cancelar.mutate(a.id, {
                      onSuccess: () => showToast({ title: 'Assinatura cancelada', variant: 'info' }),
                      onError: (err) =>
                        showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
                    })
                  }
                >
                  Cancelar
                </Button>
              )}
            </Card>
          ))
        )}
      </div>
    </AppLayout>
  );
}
