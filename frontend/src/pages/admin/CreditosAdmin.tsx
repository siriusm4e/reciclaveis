import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { centsToBRL } from '@/utils/currency';
import type { PacoteCredito } from '@/types/api';

export default function CreditosAdmin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'pacotes'],
    queryFn: adminApi.creditos.listarPacotes,
  });
  const criar = useMutation({
    mutationFn: adminApi.creditos.criarPacote,
    onSuccess: () => {
      showToast({ title: 'Pacote criado', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'pacotes'] });
    },
  });
  const ajuste = useMutation({
    mutationFn: (p: { conta_id: string; valor: number; descricao: string }) =>
      adminApi.creditos.ajuste(p.conta_id, p.valor, p.descricao),
    onSuccess: () => showToast({ title: 'Ajuste registrado', variant: 'success' }),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tighter">Créditos</h1>

      <section>
        <h2 className="font-bold mb-2">Novo pacote</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            criar.mutate({
              nome: String(fd.get('nome')),
              creditos: Number(fd.get('creditos')),
              bonus: Number(fd.get('bonus') ?? 0),
              preco_centavos: Number(fd.get('preco_centavos')),
              ordem: 100,
              ativo: true,
            });
            (e.target as HTMLFormElement).reset();
          }}
          className="grid grid-cols-1 md:grid-cols-4 gap-3"
        >
          <Input name="nome" required placeholder="Nome do pacote" />
          <Input name="creditos" type="number" required placeholder="Créditos" />
          <Input name="bonus" type="number" placeholder="Bônus" defaultValue={0} />
          <Input name="preco_centavos" type="number" required placeholder="Preço (centavos)" />
          <div className="md:col-span-4"><Button type="submit" loading={criar.isPending}>Criar</Button></div>
        </form>

        {isLoading ? <CenterSpinner /> : (
          <div className="space-y-2 mt-4">
            {(data as PacoteCredito[])?.map((p) => (
              <Card key={p.id} className="p-3 flex items-center justify-between">
                <div>
                  <p className="font-bold">{p.nome}</p>
                  <p className="text-xs">{p.creditos} + {p.bonus} bônus</p>
                </div>
                <p className="font-mono">{centsToBRL(p.preco_centavos)}</p>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="font-bold mb-2">Ajuste manual de saldo</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            ajuste.mutate({
              conta_id: String(fd.get('conta_id')),
              valor: Number(fd.get('valor')),
              descricao: String(fd.get('descricao')),
            });
          }}
          className="grid grid-cols-1 md:grid-cols-3 gap-3"
        >
          <div><Label>Conta ID</Label><Input name="conta_id" required className="font-mono" /></div>
          <div><Label>Valor (+/-)</Label><Input name="valor" type="number" required className="font-mono" /></div>
          <div><Label>Descrição</Label><Input name="descricao" required /></div>
          <div className="md:col-span-3"><Button type="submit" loading={ajuste.isPending}>Registrar ajuste</Button></div>
        </form>
      </section>
    </div>
  );
}
