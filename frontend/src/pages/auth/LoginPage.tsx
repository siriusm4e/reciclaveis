import { useState } from 'react';
import { Link } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { MobileFrame } from '@/components/MobileFrame';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { useLogin } from '@/hooks/useAuth';
import { useAuthStore } from '@/store/authStore';

export default function LoginPage() {
  const mfaRequired = useAuthStore((s) => s.mfaRequired);
  const setMfa = useAuthStore((s) => s.setMfaRequired);

  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [mfa, setMfaCode] = useState('');

  const login = useLogin();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login.mutate(
      { email, senha, mfa_code: mfa || undefined },
      {
        onError: (err) => {
          if (!useAuthStore.getState().mfaRequired) {
            showToast({ title: 'Falha no login', description: extractErrorMessage(err), variant: 'error' });
          }
        },
      },
    );
  };

  return (
    <MobileFrame>
      <div className="flex flex-1 flex-col px-screen-x pb-12 pt-12">
        <div className="mb-10 text-center">
          <p className="font-mono text-xs tracking-widest text-primary-700">PNR</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tighter text-neutral-900">
            Plataforma Nacional<br />de Resíduos
          </h1>
          <p className="mt-3 font-serif italic text-base text-neutral-600">
            Conecte-se ao mercado nacional de recicláveis.
          </p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <Label htmlFor="senha">Senha</Label>
            <Input
              id="senha"
              type="password"
              autoComplete="current-password"
              required
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {mfaRequired && (
            <div>
              <Label htmlFor="mfa">Código MFA (6 dígitos)</Label>
              <Input
                id="mfa"
                inputMode="numeric"
                pattern="\d{6}"
                maxLength={6}
                value={mfa}
                onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
                placeholder="123456"
                className="font-mono tracking-widest text-center"
              />
            </div>
          )}

          <Button type="submit" loading={login.isPending} className="w-full">
            Entrar
          </Button>
        </form>

        <div className="mt-6 text-center">
          <Link to="/auth/cadastro" className="text-sm text-primary-700 hover:underline">
            Não tem conta? <span className="font-semibold">Cadastre-se</span>
          </Link>
        </div>

        {mfaRequired && (
          <button
            type="button"
            onClick={() => setMfa(false)}
            className="mt-3 text-xs text-neutral-500 hover:text-neutral-700"
          >
            Desabilitar MFA neste login
          </button>
        )}
      </div>
    </MobileFrame>
  );
}
