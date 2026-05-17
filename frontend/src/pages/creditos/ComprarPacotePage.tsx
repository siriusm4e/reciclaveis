import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useComprarPacote, usePacotesCredito } from '@/hooks/useCreditos';
import type { ID, PagamentoMetodo } from '@/types/api';
import { centsToBRL, formatNumber } from '@/utils/currency';

export default function ComprarPacotePage() {
  const navigate = useNavigate();
  const { data, isLoading } = usePacotesCredito();
  const comprar = useComprarPacote();
  const [metodo, setMetodo] = useState<PagamentoMetodo>('pix');

  const onComprar = (id: ID) => {
    comprar.mutate(
      { pacote_id: id, metodo },
      {
        onSuccess: () => {
          showToast({ title: 'Compra realizada', variant: 'success' });
          navigate('/creditos');
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Comprar Créditos" />
      <div className="px-screen-x py-4 space-y-3">
        <div>
          <Select value={metodo} onValueChange={(v) => setMetodo(v as PagamentoMetodo)}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="pix">PIX</SelectItem>
              <SelectItem value="cartao">Cartão</SelectItem>
              <SelectItem value="boleto">Boleto</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState titulo="Sem pacotes disponíveis" />
        ) : (
          data.map((p) => (
            <Card key={p.id} className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold tracking-tight">{p.nome}</h3>
                  <p className="text-xs text-neutral-500">{p.descricao}</p>
                  <p className="mt-1 text-sm">
                    <span className="font-mono font-bold">{formatNumber(p.creditos)}</span> créditos
                    {p.bonus > 0 && (
                      <span className="ml-1 text-accent-600">+{formatNumber(p.bonus)} bônus</span>
                    )}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-mono font-bold text-primary-700">{centsToBRL(p.preco_centavos)}</p>
                  <Button size="sm" className="mt-2" onClick={() => onComprar(p.id)} loading={comprar.isPending}>
                    Comprar
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </AppLayout>
  );
}
