import { useState } from 'react';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { CenterSpinner, EmptyState, ErrorState } from '@/components/ui/states';
import { useMapaInstitucional } from '@/hooks/useInstitucional';

export default function MapaInstitucionalPage() {
  const [ibge, setIbge] = useState('');
  const { data, isLoading, error } = useMapaInstitucional(ibge.length === 7 ? ibge : null);

  return (
    <AppLayout>
      <TopBar title="Mapa institucional" />
      <div className="px-screen-x py-4 space-y-3">
        <div>
          <Input
            placeholder="IBGE (7 dígitos) — restrito ao seu escopo"
            className="font-mono"
            value={ibge}
            onChange={(e) => setIbge(e.target.value.replace(/\D/g, '').slice(0, 7))}
          />
          <p className="text-xs text-neutral-500 mt-1">
            Disponível apenas para contas Órgão Público dentro do próprio escopo territorial.
          </p>
        </div>
        {ibge.length === 7 && (isLoading ? <CenterSpinner /> : error ? <ErrorState /> : !data?.celulas.length ? (
          <EmptyState titulo="Sem dados para este território" />
        ) : (
          <div className="space-y-2">
            {data.celulas.map((c) => (
              <Card key={c.bairro} className="p-3">
                <p className="font-semibold">{c.bairro}</p>
                <div className="grid grid-cols-3 gap-2 mt-2 text-center">
                  <Cell label="Pedidos" value={c.pedidos_abertos} />
                  <Cell label="Anúncios" value={c.anuncios_ativos} />
                  <Cell label="Campanhas" value={c.campanhas_ativas} />
                </div>
              </Card>
            ))}
          </div>
        ))}
      </div>
    </AppLayout>
  );
}

function Cell({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <p className="font-mono text-2xl font-bold text-primary-700">{value}</p>
      <p className="text-[10px] uppercase tracking-wider text-neutral-500">{label}</p>
    </div>
  );
}
