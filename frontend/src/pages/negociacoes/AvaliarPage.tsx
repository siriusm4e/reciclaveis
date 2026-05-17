import { Star } from 'lucide-react';
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { showToast } from '@/components/ui/toaster';
import { useAvaliar } from '@/hooks/useNegociacao';
import type { PapelTipo } from '@/types/api';

const PAPEIS: PapelTipo[] = [
  'catador', 'coletor', 'acumulador', 'comprador', 'gestor_residuos',
  'prestador_servico', 'freteiro', 'revendedor_equipamentos', 'gerador_industrial',
];

export default function AvaliarPage() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const avaliar = useAvaliar(id);
  const [nota, setNota] = useState(5);
  const [papel, setPapel] = useState<PapelTipo>('comprador');
  const [coment, setComent] = useState('');

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    avaliar.mutate(
      { nota, papel_avaliado: papel, comentario: coment || undefined },
      {
        onSuccess: () => {
          showToast({ title: 'Avaliação registrada', description: 'Visível após reciprocidade ou 14 dias.', variant: 'success' });
          navigate(`/negociacoes/${id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Avaliar" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4">
        <div>
          <Label>Nota</Label>
          <div className="flex justify-center gap-1 mt-2">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setNota(n)}
                className="tap-target"
                aria-label={`${n} estrelas`}
              >
                <Star
                  className={`h-9 w-9 transition-colors ${n <= nota ? 'fill-accent-500 text-accent-500' : 'text-neutral-300'}`}
                />
              </button>
            ))}
          </div>
          <p className="text-center text-xs text-neutral-500 mt-1 font-mono">{nota} / 5</p>
        </div>
        <div>
          <Label>Papel da contraparte</Label>
          <Select value={papel} onValueChange={(v) => setPapel(v as PapelTipo)}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {PAPEIS.map((p) => (
                <SelectItem key={p} value={p}>{p.replace('_', ' ')}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Comentário (opcional)</Label>
          <Textarea value={coment} onChange={(e) => setComent(e.target.value)} />
        </div>
        <Button type="submit" loading={avaliar.isPending} className="w-full">Enviar avaliação</Button>
        <p className="text-xs text-neutral-500 text-center">
          Sua nota fica oculta até a contraparte avaliar ou até 14 dias.
        </p>
      </form>
    </AppLayout>
  );
}
