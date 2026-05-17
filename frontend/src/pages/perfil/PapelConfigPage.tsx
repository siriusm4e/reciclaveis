import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { showToast } from '@/components/ui/toaster';
import { useAtivarPapel, useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import type { PapelTipo } from '@/types/api';

const PAPEIS: PapelTipo[] = [
  'catador',
  'coletor',
  'acumulador',
  'comprador',
  'gestor_residuos',
  'prestador_servico',
  'freteiro',
  'revendedor_equipamentos',
  'gerador_industrial',
  'prefeitura',
  'orgao_estadual',
];

export default function PapelConfigPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const ativar = useAtivarPapel(conta?.id ?? '');
  const existente = papeis?.find((p) => p.id === id);

  const [escolhido, setEscolhido] = useState<PapelTipo>(existente?.papel ?? 'comprador');

  const onAtivar = () => {
    ativar.mutate(
      { papel: escolhido },
      {
        onSuccess: () => {
          showToast({ title: 'Papel ativado', variant: 'success' });
          navigate('/perfil');
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title={existente ? 'Configurar papel' : 'Ativar novo papel'} />
      <div className="px-screen-x py-4 space-y-4">
        {existente ? (
          <div className="rounded-lg bg-surface-card border border-neutral-100 p-4 shadow-xs">
            <p className="text-xs uppercase tracking-wider text-neutral-500">Papel</p>
            <p className="text-lg font-bold capitalize">{existente.papel.replace('_', ' ')}</p>
            <p className="text-xs text-neutral-500 mt-2">
              Status: <span className="uppercase font-semibold">{existente.status}</span>
            </p>
            <p className="mt-3 text-xs text-neutral-600">
              Para editar dados complementares ou enviar documentos exigidos, vá em
              {' '}
              <a href="/documentos" className="text-primary-700 underline">Documentos</a>.
            </p>
          </div>
        ) : (
          <>
            <div>
              <Label>Escolha o papel</Label>
              <Select value={escolhido} onValueChange={(v) => setEscolhido(v as PapelTipo)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {PAPEIS.map((p) => (
                    <SelectItem key={p} value={p}>{p.replace('_', ' ')}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button onClick={onAtivar} loading={ativar.isPending} className="w-full">
              Ativar papel
            </Button>
            <p className="text-xs text-neutral-500">
              Alguns papéis exigem documentos aprovados para liberar publicações em subcategorias reguladas.
            </p>
          </>
        )}
      </div>
    </AppLayout>
  );
}
