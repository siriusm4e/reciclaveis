import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import type { PerfilInternoTipo } from '@/types/api';

const PERFIS: PerfilInternoTipo[] = [
  'superadmin',
  'operador_atendimento',
  'moderador_conteudo',
  'gestor_comercial',
  'gestor_institucional',
];

export default function PerfisAdmin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['admin', 'perfis'], queryFn: adminApi.perfis.list });
  const criar = useMutation({
    mutationFn: (p: { usuario_id: string; tipo: PerfilInternoTipo }) =>
      adminApi.perfis.criar(p.usuario_id, p.tipo),
    onSuccess: () => {
      showToast({ title: 'Perfil criado', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'perfis'] });
    },
  });
  const setLim = useMutation({ mutationFn: adminApi.perfis.setLimiarCobertura, onSuccess: () => showToast({ title: 'Limiar atualizado', variant: 'success' }) });
  const setPrazo = useMutation({ mutationFn: adminApi.perfis.setPrazoOportunidade, onSuccess: () => showToast({ title: 'Prazo atualizado', variant: 'success' }) });

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold tracking-tighter mb-4">Perfis internos</h1>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            criar.mutate({
              usuario_id: String(fd.get('usuario_id')),
              tipo: String(fd.get('tipo')) as PerfilInternoTipo,
            });
            (e.target as HTMLFormElement).reset();
          }}
          className="grid grid-cols-1 md:grid-cols-3 gap-3"
        >
          <div><Label>ID do Usuário</Label><Input name="usuario_id" required className="font-mono" /></div>
          <div>
            <Label>Tipo</Label>
            <Select name="tipo" defaultValue="operador_atendimento">
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {PERFIS.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="md:col-span-3"><Button type="submit" loading={criar.isPending}>Criar perfil</Button></div>
        </form>

        {isLoading ? <CenterSpinner /> : (
          <div className="space-y-2 mt-4">
            {(data as Array<{ id: string; usuario_id: string; tipo: string; ativo: boolean }>)?.map((p) => (
              <Card key={p.id} className="p-3 flex items-center justify-between">
                <div>
                  <p className="font-mono text-xs">{p.usuario_id.slice(0, 8)}...</p>
                  <p className="font-bold">{p.tipo}</p>
                </div>
                <span className={`text-xs ${p.ativo ? 'text-success-dark' : 'text-neutral-500'}`}>
                  {p.ativo ? 'Ativo' : 'Inativo'}
                </span>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="font-bold mb-2">Limiar de cobertura (Alerta Pago)</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const v = Number(new FormData(e.currentTarget).get('valor'));
              setLim.mutate(v);
            }}
            className="flex gap-2"
          >
            <Input name="valor" type="number" min={1} max={50} defaultValue={3} className="font-mono w-24" />
            <Button type="submit" loading={setLim.isPending}>Salvar</Button>
          </form>
        </Card>
        <Card className="p-4">
          <h3 className="font-bold mb-2">Prazo mínimo Oportunidade Pública (dias úteis)</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const v = Number(new FormData(e.currentTarget).get('dias'));
              setPrazo.mutate(v);
            }}
            className="flex gap-2"
          >
            <Input name="dias" type="number" min={1} max={30} defaultValue={5} className="font-mono w-24" />
            <Button type="submit" loading={setPrazo.isPending}>Salvar</Button>
          </form>
        </Card>
      </section>
    </div>
  );
}
