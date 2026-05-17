import { MessageSquare } from 'lucide-react';
import { Link } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { EmptyState, SkeletonList } from '@/components/ui/states';
import { useNegociacoes } from '@/hooks/useNegociacao';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import { timeAgo } from '@/utils/dates';

export default function NegociacoesListPage() {
  const conta = useContaAtiva();
  const { data, isLoading } = useNegociacoes();

  return (
    <AppLayout>
      <TopBar title="Negociações" back={false} />
      <div className="px-screen-x py-4">
        {isLoading ? (
          <SkeletonList rows={3} />
        ) : !data?.length ? (
          <EmptyState
            icon={<MessageSquare className="h-8 w-8" />}
            titulo="Sem negociações"
            descricao="Inicie uma negociação a partir de um anúncio ou oferta."
          />
        ) : (
          <ul className="divide-y divide-neutral-100 rounded-lg bg-surface-card border border-neutral-100">
            {data.map((n) => {
              const ehVendedor = conta?.id === n.conta_vendedora_id;
              return (
                <li key={n.id}>
                  <Link to={`/negociacoes/${n.id}`} className="flex items-start gap-3 p-3 hover:bg-neutral-50 transition-colors">
                    <div className={`h-10 w-10 rounded-full ${ehVendedor ? 'bg-primary-100 text-primary-700' : 'bg-accent-500/15 text-accent-600'} flex items-center justify-center font-bold`}>
                      {ehVendedor ? 'V' : 'C'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-sm font-semibold truncate">
                          {n.publicacao_tipo.replace('_', ' ')}
                        </p>
                        <StatusBadge status={n.status} />
                      </div>
                      {n.ultima_mensagem_preview && (
                        <p className="mt-0.5 font-serif italic text-sm text-neutral-600 truncate">
                          {n.ultima_mensagem_preview}
                        </p>
                      )}
                      <p className="mt-0.5 font-mono text-[10px] text-neutral-400">
                        {timeAgo(n.ultima_mensagem_em ?? n.created_at)}
                      </p>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </AppLayout>
  );
}
