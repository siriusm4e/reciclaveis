import { useState } from 'react';
import { useParams } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useOportunidade, useSubmeterProposta } from '@/hooks/useNegociacao';
import { formatBRL } from '@/utils/currency';
import { formatDateTime } from '@/utils/dates';

export default function OportunidadeDetalhePage() {
  const { id = '' } = useParams();
  const { data, isLoading, error, refetch } = useOportunidade(id);
  const submit = useSubmeterProposta(id);
  const [valor, setValor] = useState('');
  const [condicoes, setCondicoes] = useState('');

  if (isLoading) return <AppLayout><CenterSpinner /></AppLayout>;
  if (error || !data) return <AppLayout><ErrorState onRetry={refetch} /></AppLayout>;

  const prazoEncerrado = new Date(data.prazo_submissao).getTime() < Date.now();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submit.mutate(
      { valor: Number(valor), condicoes: condicoes || undefined, documentos_anexos: [] },
      {
        onSuccess: () => {
          showToast({ title: 'Proposta submetida', variant: 'success' });
          setValor('');
          setCondicoes('');
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Oportunidade" />
      <div className="px-screen-x py-4 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-2xl font-bold tracking-tighter">{data.titulo}</h1>
          <StatusBadge status={data.status} />
        </div>
        <p className="text-xs uppercase tracking-wider text-neutral-500">{data.tipo.replace('_', ' ')}</p>
        <p className="font-serif italic text-neutral-700">{data.descricao}</p>

        {data.valor_estimado && (
          <p className="font-mono text-base">Valor estimado: <strong>{formatBRL(data.valor_estimado)}</strong></p>
        )}
        <p className="font-mono text-sm">Prazo: {formatDateTime(data.prazo_submissao)}</p>

        {data.documentos_exigidos.length > 0 && (
          <div className="rounded-lg bg-warning-light p-3 text-xs text-warning-dark">
            <p className="font-semibold mb-1">Documentos exigidos:</p>
            <ul className="font-mono list-disc list-inside">
              {data.documentos_exigidos.map((d) => <li key={d}>{d}</li>)}
            </ul>
          </div>
        )}

        {!prazoEncerrado && data.status === 'aberta_para_proposta' && (
          <form onSubmit={onSubmit} className="space-y-3 rounded-lg bg-surface-card border border-neutral-100 p-4 shadow-xs">
            <h3 className="font-bold tracking-tight">Submeter proposta</h3>
            <div>
              <Label>Valor (R$)</Label>
              <Input
                type="number"
                step="0.01"
                required
                value={valor}
                onChange={(e) => setValor(e.target.value)}
                className="font-mono"
              />
            </div>
            <div>
              <Label>Condições</Label>
              <Textarea value={condicoes} onChange={(e) => setCondicoes(e.target.value)} />
            </div>
            <Button type="submit" loading={submit.isPending} className="w-full">Enviar proposta</Button>
          </form>
        )}
      </div>
    </AppLayout>
  );
}
