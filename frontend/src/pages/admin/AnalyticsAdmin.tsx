import { useQuery } from '@tanstack/react-query';
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { adminApi } from '@/api/endpoints/moderacao';
import { Card } from '@/components/ui/card';
import { CenterSpinner } from '@/components/ui/states';

export default function AnalyticsAdmin() {
  const pub = useQuery({ queryKey: ['admin', 'pub'], queryFn: adminApi.analytics.publicacoes });
  const liq = useQuery({ queryKey: ['admin', 'liq'], queryFn: adminApi.analytics.liquidez });

  const data = (pub.data as Array<{ nome: string; total: number }>) ?? [];

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Analytics</h1>
      <a href="/api/admin/analytics/exportar-csv?relatorio=liquidez" className="text-primary-700 underline text-sm">
        Exportar liquidez (CSV)
      </a>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <Card className="p-4">
          <h2 className="font-bold mb-3">Publicações ativas por subcategoria</h2>
          {pub.isLoading ? <CenterSpinner /> : (
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={data}>
                  <XAxis dataKey="nome" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="total" fill="#1e8c4e" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
        <Card className="p-4">
          <h2 className="font-bold mb-3">Liquidez (ofertas / demandas)</h2>
          {liq.isLoading ? <CenterSpinner /> : (
            <ul className="text-sm space-y-1 max-h-72 overflow-y-auto">
              {((liq.data as Array<{ subcategoria_id: string; ofertas: number; demandas: number; razao: number | null }>) ?? []).map((r) => (
                <li key={r.subcategoria_id} className="flex items-center justify-between border-b border-neutral-100 py-1">
                  <span className="font-mono text-xs">{r.subcategoria_id.slice(0, 8)}</span>
                  <span className="font-mono">{r.ofertas} / {r.demandas}</span>
                  <span className="font-mono">{r.razao?.toFixed(2) ?? '—'}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
