import { Trash2 } from 'lucide-react';
import { useState } from 'react';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useContaAtiva, useConvidarMembro, useMembros, useRemoverMembro } from '@/hooks/useContaAtiva';
import type { PapelInternoMembro } from '@/types/api';

export default function MembrosPage() {
  const conta = useContaAtiva();
  const { data: membros, isLoading } = useMembros(conta?.id ?? null);
  const convidar = useConvidarMembro(conta?.id ?? '');
  const remover = useRemoverMembro(conta?.id ?? '');
  const [email, setEmail] = useState('');
  const [papel, setPapel] = useState<PapelInternoMembro>('operador');

  if (!conta) return null;

  const onConvidar = (e: React.FormEvent) => {
    e.preventDefault();
    convidar.mutate(
      { email, papel_interno: papel },
      {
        onSuccess: () => {
          showToast({ title: 'Convite enviado', description: `Expira em 48h.`, variant: 'success' });
          setEmail('');
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Membros" />
      <div className="px-screen-x py-4 space-y-4">
        {conta.tipo === 'pf' && (
          <div className="rounded-lg bg-info-light p-3 text-sm text-info-dark">
            Conta PF tem admin único — sem convites.
          </div>
        )}

        {conta.tipo !== 'pf' && (
          <form onSubmit={onConvidar} className="space-y-2 rounded-lg bg-surface-card border border-neutral-100 p-3 shadow-xs">
            <h3 className="text-sm font-bold">Convidar membro</h3>
            <div>
              <Label>E-mail</Label>
              <Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div>
              <Label>Papel interno</Label>
              <Select value={papel} onValueChange={(v) => setPapel(v as PapelInternoMembro)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="operador">Operador</SelectItem>
                  <SelectItem value="leitor">Leitor</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" loading={convidar.isPending} className="w-full">Convidar</Button>
            <p className="text-xs text-neutral-500">
              O convite expira em 48h. Reenviar para o mesmo e-mail cancela o anterior.
            </p>
          </form>
        )}

        {isLoading ? (
          <CenterSpinner />
        ) : !membros?.length ? (
          <EmptyState titulo="Sem membros" />
        ) : (
          <div className="space-y-2">
            {membros.map((m) => (
              <Card key={m.id} className="flex items-center justify-between p-3">
                <div>
                  <p className="text-sm font-mono">{m.usuario_id.slice(0, 8)}...</p>
                  <p className="text-xs uppercase tracking-wider text-neutral-500">{m.papel_interno}</p>
                </div>
                {conta.tipo !== 'pf' && (
                  <button
                    type="button"
                    onClick={() =>
                      remover.mutate(m.id, {
                        onSuccess: () => showToast({ title: 'Membro removido', variant: 'info' }),
                        onError: (err) =>
                          showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
                      })
                    }
                    className="rounded-full p-2 text-error hover:bg-error-light"
                    aria-label="Remover"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
