import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { StatusBadge } from '@/components/StatusBadge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import type { Conta, ContaStatus } from '@/types/api';

export default function ContasAdmin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'contas'],
    queryFn: () => adminApi.contas.list({ page: 1, page_size: 100 }),
  });

  const mudar = useMutation({
    mutationFn: (p: { id: string; status: string; motivo: string }) =>
      adminApi.contas.mudarStatus(p.id, p.status, p.motivo),
    onSuccess: () => {
      showToast({ title: 'Status atualizado', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'contas'] });
      setEdit(null);
    },
  });

  const [edit, setEdit] = useState<Conta | null>(null);
  const [novo, setNovo] = useState<ContaStatus>('ativa');
  const [motivo, setMotivo] = useState('');

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Contas</h1>
      {isLoading ? <CenterSpinner /> : (
        <div className="space-y-2">
          {(data as Conta[])?.map((c) => (
            <Card key={c.id} className="p-3 flex items-center justify-between">
              <div className="min-w-0">
                <p className="font-bold truncate">{c.nome_publico}</p>
                <p className="text-xs text-neutral-500">{c.tipo} · CNPJ {c.cnpj ?? '—'}</p>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={c.status} />
                <Button size="sm" variant="ghost" onClick={() => { setEdit(c); setNovo(c.status); }}>
                  Mudar
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={!!edit} onOpenChange={(v) => !v && setEdit(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mudar status — {edit?.nome_publico}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Novo status</Label>
              <Select value={novo} onValueChange={(v) => setNovo(v as ContaStatus)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {['pendente', 'em_revisao', 'ativa', 'suspensa', 'anonimizada'].map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Motivo (obrigatório)</Label>
              <Input value={motivo} onChange={(e) => setMotivo(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setEdit(null)}>Cancelar</Button>
            <Button
              onClick={() => edit && mudar.mutate({ id: edit.id, status: novo, motivo })}
              loading={mudar.isPending}
            >
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
