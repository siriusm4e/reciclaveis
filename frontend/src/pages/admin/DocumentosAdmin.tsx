import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi } from '@/api/endpoints/moderacao';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import type { Documento } from '@/types/api';
import { formatDate } from '@/utils/dates';

export default function DocumentosAdmin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['admin', 'doc-fila'], queryFn: adminApi.documentos.fila });
  const aprovar = useMutation({
    mutationFn: (id: string) => adminApi.documentos.aprovar(id),
    onSuccess: () => {
      showToast({ title: 'Aprovado', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'doc-fila'] });
    },
  });
  const rejeitar = useMutation({
    mutationFn: (p: { id: string; motivo: string }) => adminApi.documentos.rejeitar(p.id, p.motivo),
    onSuccess: () => {
      showToast({ title: 'Rejeitado', variant: 'info' });
      qc.invalidateQueries({ queryKey: ['admin', 'doc-fila'] });
      setRej(null);
    },
  });
  const [rej, setRej] = useState<string | null>(null);
  const [motivo, setMotivo] = useState('');

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tighter mb-6">Fila de aprovação</h1>
      {isLoading ? <CenterSpinner /> : !(data as Documento[])?.length ? (
        <EmptyState titulo="Fila vazia" />
      ) : (
        <div className="space-y-2">
          {(data as Documento[]).map((d) => (
            <Card key={d.id} className="p-4 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="font-mono text-xs text-neutral-500">{d.id.slice(0, 8)}...</p>
                <p className="font-semibold">Tipo: {d.tipo_documento_id.slice(0, 8)}...</p>
                <p className="text-xs">Número: {d.numero ?? '—'} · Venc: {d.data_vencimento ? formatDate(d.data_vencimento) : '—'}</p>
                <a href={`/storage/${d.arquivo_path}`} target="_blank" rel="noreferrer" className="text-primary-700 underline text-xs">
                  Abrir arquivo
                </a>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="primary" onClick={() => aprovar.mutate(d.id)} loading={aprovar.isPending}>
                  Aprovar
                </Button>
                <Button size="sm" variant="danger" onClick={() => setRej(d.id)}>
                  Rejeitar
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={!!rej} onOpenChange={(v) => !v && setRej(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Motivo da rejeição</DialogTitle></DialogHeader>
          <div>
            <Label>Motivo (obrigatório)</Label>
            <Input value={motivo} onChange={(e) => setMotivo(e.target.value)} />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setRej(null)}>Voltar</Button>
            <Button
              variant="danger"
              onClick={() => rej && rejeitar.mutate({ id: rej, motivo })}
              loading={rejeitar.isPending}
            >
              Confirmar rejeição
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
