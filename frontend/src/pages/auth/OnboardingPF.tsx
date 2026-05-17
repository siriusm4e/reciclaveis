import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { MobileFrame } from '@/components/MobileFrame';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { useCriarConta } from '@/hooks/useContaAtiva';

export default function OnboardingPF() {
  const navigate = useNavigate();
  const criar = useCriarConta();
  const [nome, setNome] = useState('');

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      { tipo: 'pf', nome_publico: nome },
      {
        onSuccess: () => {
          showToast({ title: 'Conta criada', description: 'Bem-vindo à PNR!', variant: 'success' });
          navigate('/home');
        },
        onError: (err) =>
          showToast({ title: 'Erro', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <MobileFrame>
      <TopBar title="Conta Pessoa Física" />
      <div className="px-screen-x py-6 space-y-4">
        <p className="text-sm text-neutral-700">
          Sua Conta PF será criada com você como administrador único.
        </p>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label htmlFor="nome">Nome público</Label>
            <Input
              id="nome"
              required
              minLength={2}
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              placeholder="Como quer aparecer na plataforma"
            />
          </div>
          <Button type="submit" loading={criar.isPending} className="w-full">
            Criar minha Conta
          </Button>
        </form>
      </div>
    </MobileFrame>
  );
}
