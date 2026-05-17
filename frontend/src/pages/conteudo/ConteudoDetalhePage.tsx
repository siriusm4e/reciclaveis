import { useParams } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { useConteudo } from '@/hooks/useConteudo';

export default function ConteudoDetalhePage() {
  const { id = '' } = useParams();
  const { data, isLoading, error, refetch } = useConteudo(id);

  if (isLoading) return <AppLayout><CenterSpinner /></AppLayout>;
  if (error || !data) return <AppLayout><ErrorState onRetry={refetch} /></AppLayout>;

  return (
    <AppLayout>
      <TopBar title={data.tipo.toUpperCase()} />
      <article className="px-screen-x py-4 space-y-4">
        {data.capa_path && (
          <img src={data.capa_path} alt="" className="w-full aspect-[16/9] object-cover rounded-lg" />
        )}
        <h1 className="text-2xl font-bold tracking-tighter">{data.titulo}</h1>
        {data.resumo && <p className="font-serif italic text-base text-neutral-700">{data.resumo}</p>}
        {data.url && (
          <a href={data.url} target="_blank" rel="noreferrer" className="text-primary-700 underline">
            Abrir link externo →
          </a>
        )}
        {data.conteudo && (
          <div
            className="prose prose-sm max-w-none text-neutral-800"
            // O backend sanitiza com bleach antes de devolver
            dangerouslySetInnerHTML={{ __html: data.conteudo }}
          />
        )}
      </article>
    </AppLayout>
  );
}
