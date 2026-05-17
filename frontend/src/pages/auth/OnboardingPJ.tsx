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
import { maskCNPJ } from '@/utils/currency';

export default function OnboardingPJ() {
  const navigate = useNavigate();
  const criar = useCriarConta();
  const [form, setForm] = useState({ nome_publico: '', cnpj: '' });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      { tipo: 'pj_privada', nome_publico: form.nome_publico, cnpj: form.cnpj.replace(/\D/g, '') },
      {
        onSuccess: () => {
          showToast({
            title: 'Conta PJ criada',
            description: 'Próximos passos: ativar Papéis, anexar documentos, convidar Membros.',
            variant: 'success',
          });
          navigate('/perfil');
        },
        onError: (err) =>
          showToast({ title: 'Erro', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <MobileFrame>
      <TopBar title="Conta Pessoa Jurídica" />
      <div className="px-screen-x py-6 space-y-4">
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label htmlFor="nome">Nome público / Razão Social</Label>
            <Input
              id="nome"
              required
              value={form.nome_publico}
              onChange={(e) => setForm({ ...form, nome_publico: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="cnpj">CNPJ</Label>
            <Input
              id="cnpj"
              required
              inputMode="numeric"
              value={maskCNPJ(form.cnpj)}
              onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
              className="font-mono"
            />
          </div>
          <p className="text-xs text-neutral-500">
            Você poderá ativar Papéis (Comprador, Gestor de Resíduos, Freteiro, etc.) e convidar
            membros logo após criar a Conta.
          </p>
          <Button type="submit" loading={criar.isPending} className="w-full">
            Criar Conta PJ
          </Button>
        </form>
      </div>
    </MobileFrame>
  );
}
