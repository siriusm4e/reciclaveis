import { Briefcase } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { EmptyState, SkeletonList } from '@/components/ui/states';
import { useOportunidades } from '@/hooks/useNegociacao';
import { formatBRL } from '@/utils/currency';
import { formatDateTime } from '@/utils/dates';

export default function OportunidadesListPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useOportunidades();
  return (
    <AppLayout>
      <TopBar title="Oportunidades" action={
        <Button size="sm" variant="ghost" onClick={() => navigate('/oportunidades/criar')}>Nova</Button>
      } />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <SkeletonList rows={3} />
        ) : !data?.length ? (
          <EmptyState
            icon={<Briefcase className="h-8 w-8" />}
            titulo="Sem oportunidades abertas"
          />
        ) : (
          <div className="space-y-3">
            {data.map((o) => (
              <Link key={o.id} to={`/oportunidades/${o.id}`} className="block">
                <Card className="p-4 hover:bg-neutral-50 transition-colors">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-bold tracking-tight">{o.titulo}</h3>
                    <StatusBadge status={o.status} />
                  </div>
                  <p className="mt-1 text-xs text-neutral-600 uppercase tracking-wider">{o.tipo.replace('_', ' ')}</p>
                  {o.valor_estimado && (
                    <p className="mt-2 font-mono text-sm">Estimado: {formatBRL(o.valor_estimado)}</p>
                  )}
                  <p className="mt-1 text-xs text-neutral-500 font-mono">
                    Prazo: {formatDateTime(o.prazo_submissao)}
                  </p>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
