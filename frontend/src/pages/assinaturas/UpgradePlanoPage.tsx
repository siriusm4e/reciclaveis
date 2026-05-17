import { Check } from 'lucide-react';
import { useState } from 'react';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useAssinar, usePlanosPorPapel } from '@/hooks/useCreditos';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { centsToBRL } from '@/utils/currency';

export default function UpgradePlanoPage() {
  const conta = useContaAtiva();
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const [papelId, setPapelId] = useState<string>('');
  const papel = papeis?.find((p) => p.id === papelId);
  const { data: planos, isLoading } = usePlanosPorPapel(papel?.papel ?? null);
  const assinar = useAssinar();

  const onAssinar = (planoId: string) => {
    if (!papelId) return;
    assinar.mutate(
      { papel_id: papelId, plano_id: planoId },
      {
        onSuccess: () => showToast({ title: 'Plano contratado', variant: 'success' }),
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Planos" />
      <div className="px-screen-x py-4 space-y-3">
        <div>
          <Label>Papel ativo</Label>
          <Select value={papelId} onValueChange={setPapelId}>
            <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
            <SelectContent>
              {papeis?.filter((p) => p.status === 'ativo').map((p) => (
                <SelectItem key={p.id} value={p.id}>{p.papel.replace('_', ' ')}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {!papelId ? (
          <p className="text-sm text-neutral-500">Selecione um papel para ver os planos disponíveis.</p>
        ) : isLoading ? (
          <CenterSpinner />
        ) : !planos?.length ? (
          <EmptyState titulo="Sem planos cadastrados para este Papel" />
        ) : (
          planos.map((p) => (
            <Card key={p.id} className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold tracking-tight">{p.nome}</h3>
                  {p.descricao && <p className="text-xs text-neutral-600">{p.descricao}</p>}
                </div>
                <p className="font-mono font-bold text-primary-700">
                  {p.gratuito ? 'Grátis' : centsToBRL(p.preco_mensal_centavos) + '/mês'}
                </p>
              </div>
              <ul className="mt-3 space-y-1 text-sm">
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary-600" /> Até {p.limite_publicacoes_ativas} publicações ativas</li>
                {p.permite_alerta_pago && (
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary-600" /> Alerta Pago disponível</li>
                )}
              </ul>
              <Button onClick={() => onAssinar(p.id)} loading={assinar.isPending} className="mt-3 w-full">
                Contratar
              </Button>
            </Card>
          ))
        )}
      </div>
    </AppLayout>
  );
}
