import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { centsToBRL } from '@/utils/currency';
import type { Plano } from '@/types/api';

export default function AssinaturasAdmin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['admin', 'planos'], queryFn: adminApi.assinaturas.planos });
  const criar = useMutation({
    mutationFn: adminApi.assinaturas.criarPlano,
    onSuccess: () => {
      showToast({ title: 'Plano criado', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'planos'] });
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tighter">Planos e Assinaturas</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          criar.mutate({
            papel: String(fd.get('papel')),
            nome: String(fd.get('nome')),
            limite_publicacoes_ativas: Number(fd.get('limite')),
            permite_alerta_pago: fd.get('alerta') === 'on',
            preco_mensal_centavos: Number(fd.get('preco_centavos')),
            gratuito: fd.get('gratuito') === 'on',
            ativo: true,
          });
          (e.target as HTMLFormElement).reset();
        }}
        className="grid grid-cols-1 md:grid-cols-4 gap-3"
      >
        <Input name="papel" required placeholder="Papel (slug)" />
        <Input name="nome" required placeholder="Nome do plano" />
        <Input name="limite" required type="number" placeholder="Limite publicações" />
        <Input name="preco_centavos" type="number" required placeholder="Preço/mês (centavos)" />
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="alerta" /> Permite Alerta Pago</label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="gratuito" /> Gratuito</label>
        <div className="md:col-span-4"><Button type="submit" loading={criar.isPending}>Criar plano</Button></div>
      </form>

      {isLoading ? <CenterSpinner /> : (
        <div className="space-y-2">
          {(data as Plano[])?.map((p) => (
            <Card key={p.id} className="p-3">
              <p className="font-bold">{p.nome} — <span className="font-mono">{p.papel}</span></p>
              <p className="text-xs">{p.limite_publicacoes_ativas} publicações · {p.permite_alerta_pago ? 'com Alerta' : 'sem Alerta'} · {p.gratuito ? 'Grátis' : centsToBRL(p.preco_mensal_centavos)}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
