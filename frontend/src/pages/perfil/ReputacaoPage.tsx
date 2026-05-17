import { Star } from 'lucide-react';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import { useReputacao } from '@/hooks/useNegociacao';

export default function ReputacaoPage() {
  const conta = useContaAtiva();
  const { data, isLoading } = useReputacao(conta?.id ?? null);

  return (
    <AppLayout>
      <TopBar title="Reputação" />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.por_papel.length ? (
          <EmptyState
            icon={<Star className="h-8 w-8" />}
            titulo="Sem avaliações ainda"
            descricao="Conclua negociações para receber avaliações."
          />
        ) : (
          <div className="space-y-3">
            {data.por_papel.map((p) => (
              <Card key={p.papel} className="p-4">
                <div className="flex items-center justify-between">
                  <h3 className="capitalize text-base font-bold tracking-tight">{p.papel.replace('_', ' ')}</h3>
                  <span className="font-mono font-bold text-2xl text-accent-600">{p.media.toFixed(1)}</span>
                </div>
                <p className="text-xs text-neutral-500 font-mono">{p.total_avaliacoes} avaliações</p>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
