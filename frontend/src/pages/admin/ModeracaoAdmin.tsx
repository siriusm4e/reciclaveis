import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { StatusBadge } from '@/components/StatusBadge';
import { showToast } from '@/components/ui/toaster';
import type { AcaoModeracao, Denuncia } from '@/types/api';

export default function ModeracaoAdmin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['admin', 'denuncias'], queryFn: () => adminApi.moderacao.fila(1, 100) });
  const decidir = useMutation({
    mutationFn: (p: { id: string; acao: AcaoModeracao; motivo: string }) =>
      adminApi.moderacao.decidir(p.id, p.acao, p.motivo),
    onSuccess: () => {
      showToast({ title: 'Decisão registrada', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'denuncias'] });
      setSel(null);
    },
  });
  const [sel, setSel] = useState<Denuncia | null>(null);
  const [acao, setAcao] = useState<AcaoModeracao>('arquivar');
  const [motivo, setMotivo] = useState('');

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Moderação</h1>
      {isLoading ? <CenterSpinner /> : !(data as Denuncia[])?.length ? (
        <EmptyState titulo="Fila vazia" />
      ) : (
        <div className="space-y-2">
          {(data as Denuncia[]).map((d) => (
            <Card key={d.id} className="p-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wider text-neutral-500">{d.alvo_tipo} · {d.tipo_fechado}</p>
                  <p className="font-mono text-xs">{d.alvo_id.slice(0, 8)}...</p>
                  <p className="text-sm mt-1">{d.descricao}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={d.status} />
                  <Button size="sm" onClick={() => setSel(d)}>Decidir</Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={!!sel} onOpenChange={(v) => !v && setSel(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Decidir denúncia</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Ação</Label>
              <Select value={acao} onValueChange={(v) => setAcao(v as AcaoModeracao)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {(['arquivar', 'advertir', 'ocultar', 'remover', 'suspender', 'banir'] as AcaoModeracao[]).map((a) => (
                    <SelectItem key={a} value={a}>{a}</SelectItem>
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
            <Button variant="ghost" onClick={() => setSel(null)}>Cancelar</Button>
            <Button
              variant="danger"
              onClick={() => sel && decidir.mutate({ id: sel.id, acao, motivo })}
              loading={decidir.isPending}
            >
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
