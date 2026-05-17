import { Check, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import {
  useContaAtiva,
  useMinhasContas,
  useTrocarConta,
} from '@/hooks/useContaAtiva';

export default function TrocarContaPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useMinhasContas();
  const ativa = useContaAtiva();
  const trocar = useTrocarConta();

  return (
    <AppLayout>
      <TopBar title="Minhas Contas" />
      <div className="px-screen-x py-4 space-y-3">
        <Button variant="secondary" className="w-full" onClick={() => navigate('/onboarding')}>
          <Plus className="h-4 w-4" /> Criar nova Conta
        </Button>
        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState titulo="Você ainda não tem Contas" />
        ) : (
          data.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => {
                trocar(c);
                navigate('/home');
              }}
              className="w-full text-left"
            >
              <Card className={`p-3 flex items-center justify-between transition-colors hover:bg-neutral-50 ${c.id === ativa?.id ? 'border-primary-500 bg-primary-50' : ''}`}>
                <div>
                  <p className="font-bold">{c.nome_publico}</p>
                  <p className="text-xs uppercase tracking-wider text-neutral-500">{c.tipo.replace('_', ' ')} · {c.status}</p>
                </div>
                {c.id === ativa?.id && <Check className="h-5 w-5 text-primary-700" />}
              </Card>
            </button>
          ))
        )}
      </div>
    </AppLayout>
  );
}
