import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { MobileFrame } from '@/components/MobileFrame';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { useRegister } from '@/hooks/useAuth';
import { maskCPF, maskTelefone } from '@/utils/currency';

export default function RegisterPage() {
  const navigate = useNavigate();
  const reg = useRegister();
  const [form, setForm] = useState({
    nome_completo: '',
    cpf: '',
    email: '',
    senha: '',
    telefone: '',
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    reg.mutate(
      {
        nome_completo: form.nome_completo,
        cpf: form.cpf.replace(/\D/g, ''),
        email: form.email,
        senha: form.senha,
        telefone: form.telefone.replace(/\D/g, '') || undefined,
      },
      {
        onSuccess: () => {
          showToast({
            title: 'Cadastro realizado',
            description: 'Faça login para continuar.',
            variant: 'success',
          });
          navigate('/auth/login');
        },
        onError: (err) =>
          showToast({ title: 'Falha no cadastro', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <MobileFrame>
      <TopBar title="Criar conta" />
      <div className="px-screen-x py-6">
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label htmlFor="nome">Nome completo</Label>
            <Input
              id="nome"
              required
              autoComplete="name"
              value={form.nome_completo}
              onChange={(e) => setForm({ ...form, nome_completo: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="cpf">CPF</Label>
            <Input
              id="cpf"
              required
              inputMode="numeric"
              value={maskCPF(form.cpf)}
              onChange={(e) => setForm({ ...form, cpf: e.target.value })}
              className="font-mono"
            />
          </div>
          <div>
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="senha">Senha (mín. 10 caracteres)</Label>
            <Input
              id="senha"
              type="password"
              required
              minLength={10}
              autoComplete="new-password"
              value={form.senha}
              onChange={(e) => setForm({ ...form, senha: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="tel">Telefone (opcional)</Label>
            <Input
              id="tel"
              inputMode="tel"
              autoComplete="tel"
              value={maskTelefone(form.telefone)}
              onChange={(e) => setForm({ ...form, telefone: e.target.value })}
              className="font-mono"
            />
          </div>
          <p className="text-xs text-neutral-500">
            Ao continuar, você concorda com os termos da plataforma e com o tratamento de dados conforme a LGPD.
          </p>
          <Button type="submit" loading={reg.isPending} className="w-full">
            Criar conta
          </Button>
        </form>
        <div className="mt-6 text-center">
          <Link to="/auth/login" className="text-sm text-primary-700 hover:underline">
            Já tem conta? Entrar
          </Link>
        </div>
      </div>
    </MobileFrame>
  );
}
