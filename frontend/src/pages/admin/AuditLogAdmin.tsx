import { useQuery } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { formatDateTime } from '@/utils/dates';

interface AuditEntry {
  id: string;
  created_at: string;
  acao: string;
  recurso_tipo: string;
  recurso_id: string | null;
  motivo: string | null;
  payload: Record<string, unknown>;
  admin_id: string | null;
}

export default function AuditLogAdmin() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'audit'],
    queryFn: () => adminApi.perfis.auditLog({ page: 1, page_size: 200 }),
  });

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Audit log</h1>
      {isLoading ? <CenterSpinner /> : !(data as AuditEntry[])?.length ? (
        <EmptyState titulo="Sem entradas" />
      ) : (
        <div className="space-y-2">
          {(data as AuditEntry[]).map((e) => (
            <Card key={e.id} className="p-3">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-mono text-xs text-neutral-500">{formatDateTime(e.created_at)}</p>
                  <p className="font-bold mt-1">{e.acao}</p>
                  <p className="text-xs">recurso: {e.recurso_tipo} · {e.recurso_id?.slice(0, 8) ?? '—'}</p>
                  {e.motivo && <p className="text-sm mt-1 italic">"{e.motivo}"</p>}
                </div>
                <p className="text-[10px] font-mono text-neutral-400">admin {e.admin_id?.slice(0, 8) ?? '—'}</p>
              </div>
              {Object.keys(e.payload).length > 0 && (
                <pre className="mt-2 rounded bg-neutral-100 p-2 text-[10px] font-mono overflow-x-auto">
                  {JSON.stringify(e.payload, null, 2)}
                </pre>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
