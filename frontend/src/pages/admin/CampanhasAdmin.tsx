import { useQuery } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { StatusBadge } from '@/components/StatusBadge';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import type { Campanha } from '@/types/api';

function formatData(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('pt-BR');
}

export default function CampanhasAdmin() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'campanhas'],
    queryFn: () => adminApi.campanhas.list(1, 100),
  });

  const campanhas = (data as Campanha[]) ?? [];

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Campanhas</h1>
      {isLoading ? (
        <CenterSpinner />
      ) : campanhas.length === 0 ? (
        <EmptyState titulo="Nenhuma campanha" descricao="Ainda não há campanhas cadastradas." />
      ) : (
        <div className="space-y-2">
          {campanhas.map((c) => (
            <Card key={c.id} className="p-3 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="font-bold truncate">{c.titulo}</p>
                <p className="text-xs text-neutral-500 truncate">
                  {[c.cidade, c.uf].filter(Boolean).join('/') || '—'}
                  {c.tipo_residuo ? ` · ${c.tipo_residuo}` : ''}
                  {` · evento ${formatData(c.data_evento)}`}
                </p>
              </div>
              <StatusBadge status={c.status} />
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
