import { useState } from 'react';

import { AppLayout } from '@/components/AppLayout';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { useCampanhas } from '@/hooks/useInstitucional';
import { formatDateTime } from '@/utils/dates';

export default function CampanhasPage() {
  const [ibge, setIbge] = useState('3550308');
  const { data, isLoading } = useCampanhas(ibge);

  return (
    <AppLayout>
      <TopBar title="Campanhas" />
      <div className="px-screen-x py-4 space-y-4">
        <div>
          <Input
            value={ibge}
            onChange={(e) => setIbge(e.target.value.replace(/\D/g, '').slice(0, 7))}
            placeholder="IBGE do município (7 dígitos)"
            className="font-mono"
          />
          <p className="text-xs text-neutral-500 mt-1">
            Campanhas só aparecem se sua Conta tem opt-in para comunicações da Prefeitura.
          </p>
        </div>
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState titulo="Sem campanhas publicadas neste município" />
        ) : (
          <div className="space-y-2">
            {data.map((c) => (
              <Card key={c.id} className="p-3">
                <div className="flex items-start justify-between">
                  <h3 className="font-bold tracking-tight">{c.titulo}</h3>
                  <StatusBadge status={c.status} />
                </div>
                {c.data_evento && (
                  <p className="text-xs font-mono text-neutral-500">{formatDateTime(c.data_evento)}</p>
                )}
                <p className="font-serif italic text-sm text-neutral-700 mt-2">{c.descricao}</p>
                {c.beneficio && (
                  <p className="mt-2 text-xs text-primary-700">Benefício: {c.beneficio}</p>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
