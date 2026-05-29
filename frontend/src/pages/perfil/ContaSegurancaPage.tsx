import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { extractErrorMessage } from '@/api/client';
import { usuariosApi } from '@/api/endpoints/usuarios';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { useMe } from '@/hooks/useAuth';

export default function ContaSegurancaPage() {
  const qc = useQueryClient();
  const { data: me } = useMe();

  // --- Trocar e-mail ---
  const [emailSenha, setEmailSenha] = useState('');
  const [novoEmail, setNovoEmail] = useState('');
  const alterarEmail = useMutation({
    mutationFn: () => usuariosApi.alterarEmail(emailSenha, novoEmail),
    onSuccess: () => {
      showToast({ title: 'E-mail atualizado', variant: 'success' });
      setEmailSenha('');
      setNovoEmail('');
      qc.invalidateQueries({ queryKey: ['me'] });
    },
    onError: (err) =>
      showToast({ title: 'Não foi possível trocar o e-mail', description: extractErrorMessage(err), variant: 'error' }),
  });

  // --- Trocar senha ---
  const [senhaAtual, setSenhaAtual] = useState('');
  const [novaSenha, setNovaSenha] = useState('');
  const [confirmar, setConfirmar] = useState('');
  const alterarSenha = useMutation({
    mutationFn: () => usuariosApi.alterarSenha(senhaAtual, novaSenha),
    onSuccess: () => {
      showToast({ title: 'Senha atualizada', variant: 'success' });
      setSenhaAtual('');
      setNovaSenha('');
      setConfirmar('');
    },
    onError: (err) =>
      showToast({ title: 'Não foi possível trocar a senha', description: extractErrorMessage(err), variant: 'error' }),
  });

  const senhaInvalida = novaSenha.length > 0 && novaSenha.length < 6;
  const naoConfere = confirmar.length > 0 && confirmar !== novaSenha;

  return (
    <AppLayout>
      <TopBar title="Conta e segurança" />
      <div className="px-screen-x py-4 space-y-4">
        {/* Trocar e-mail */}
        <Card className="p-4">
          <h2 className="font-bold tracking-tight mb-1">Trocar e-mail</h2>
          <p className="text-xs text-neutral-500 mb-3">E-mail atual: {me?.email ?? '—'}</p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              alterarEmail.mutate();
            }}
            className="space-y-3"
          >
            <div>
              <Label htmlFor="novo-email">Novo e-mail</Label>
              <Input
                id="novo-email"
                type="email"
                autoComplete="email"
                required
                value={novoEmail}
                onChange={(e) => setNovoEmail(e.target.value)}
                placeholder="novo@email.com"
              />
            </div>
            <div>
              <Label htmlFor="email-senha">Senha atual (confirmação)</Label>
              <Input
                id="email-senha"
                type="password"
                autoComplete="current-password"
                required
                value={emailSenha}
                onChange={(e) => setEmailSenha(e.target.value)}
                placeholder="••••••••"
              />
            </div>
            <Button type="submit" loading={alterarEmail.isPending} disabled={!novoEmail || !emailSenha}>
              Atualizar e-mail
            </Button>
          </form>
        </Card>

        {/* Trocar senha */}
        <Card className="p-4">
          <h2 className="font-bold tracking-tight mb-3">Trocar senha</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              alterarSenha.mutate();
            }}
            className="space-y-3"
          >
            <div>
              <Label htmlFor="senha-atual">Senha atual</Label>
              <Input
                id="senha-atual"
                type="password"
                autoComplete="current-password"
                required
                value={senhaAtual}
                onChange={(e) => setSenhaAtual(e.target.value)}
                placeholder="••••••••"
              />
            </div>
            <div>
              <Label htmlFor="nova-senha">Nova senha (mín. 6)</Label>
              <Input
                id="nova-senha"
                type="password"
                autoComplete="new-password"
                required
                value={novaSenha}
                onChange={(e) => setNovaSenha(e.target.value)}
                placeholder="••••••••"
              />
              {senhaInvalida && <p className="mt-1 text-xs text-error">Mínimo de 6 caracteres.</p>}
            </div>
            <div>
              <Label htmlFor="confirmar">Confirmar nova senha</Label>
              <Input
                id="confirmar"
                type="password"
                autoComplete="new-password"
                required
                value={confirmar}
                onChange={(e) => setConfirmar(e.target.value)}
                placeholder="••••••••"
              />
              {naoConfere && <p className="mt-1 text-xs text-error">As senhas não conferem.</p>}
            </div>
            <Button
              type="submit"
              loading={alterarSenha.isPending}
              disabled={!senhaAtual || senhaInvalida || naoConfere || !novaSenha || !confirmar}
            >
              Atualizar senha
            </Button>
          </form>
        </Card>
      </div>
    </AppLayout>
  );
}
