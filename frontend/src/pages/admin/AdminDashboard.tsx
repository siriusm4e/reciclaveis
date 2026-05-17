import { useQuery } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Card } from '@/components/ui/card';
import { CenterSpinner } from '@/components/ui/states';

export default function AdminDashboard() {
  const filaDoc = useQuery({ queryKey: ['admin', 'doc-fila'], queryFn: adminApi.documentos.fila });
  const denuncias = useQuery({ queryKey: ['admin', 'denuncias'], queryFn: () => adminApi.moderacao.fila(1, 50) });
  const publicacoes = useQuery({ queryKey: ['admin', 'pub'], queryFn: adminApi.analytics.publicacoes });

  if (filaDoc.isLoading) return <CenterSpinner />;

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Dashboard</h1>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-3">
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wider text-neutral-500">Documentos na fila</p>
          <p className="font-mono text-4xl font-bold text-primary-700 mt-1">{(filaDoc.data as unknown[])?.length ?? 0}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wider text-neutral-500">Denúncias abertas</p>
          <p className="font-mono text-4xl font-bold text-warning-dark mt-1">{(denuncias.data as unknown[])?.length ?? 0}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wider text-neutral-500">Publicações ativas</p>
          <p className="font-mono text-4xl font-bold text-accent-600 mt-1">
            {((publicacoes.data as Array<{ total: number }>) ?? []).reduce((a, c) => a + (c.total ?? 0), 0)}
          </p>
        </Card>
      </div>
    </div>
  );
}
