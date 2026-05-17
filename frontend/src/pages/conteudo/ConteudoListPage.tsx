import { BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { useConteudos } from '@/hooks/useConteudo';

export default function ConteudoListPage() {
  const { data, isLoading } = useConteudos();
  return (
    <AppLayout>
      <TopBar title="Aprenda" />
      <div className="px-screen-x py-4 space-y-3">
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState icon={<BookOpen className="h-8 w-8" />} titulo="Sem conteúdos publicados" />
        ) : (
          data.map((c) => (
            <Link key={c.id} to={`/conteudo/${c.id}`} className="block">
              <Card className="p-3 hover:bg-neutral-50 transition-colors">
                <p className="text-[10px] uppercase tracking-wider text-primary-700">{c.tipo}</p>
                <h3 className="font-bold tracking-tight">{c.titulo}</h3>
                {c.resumo && <p className="text-sm text-neutral-600 mt-1 font-serif italic">{c.resumo}</p>}
              </Card>
            </Link>
          ))
        )}
      </div>
    </AppLayout>
  );
}
