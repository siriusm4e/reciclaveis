import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { MobileFrame } from '@/components/MobileFrame';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useMfaSetup, useMfaVerify } from '@/hooks/useAuth';

export default function MfaSetupPage() {
  const navigate = useNavigate();
  const setup = useMfaSetup();
  const verify = useMfaVerify();
  const [code, setCode] = useState('');

  useEffect(() => {
    setup.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onVerify = (e: React.FormEvent) => {
    e.preventDefault();
    verify.mutate(code, {
      onSuccess: () => {
        showToast({ title: 'MFA ativado', variant: 'success' });
        navigate('/perfil');
      },
      onError: () => showToast({ title: 'Código inválido', variant: 'error' }),
    });
  };

  return (
    <MobileFrame>
      <TopBar title="Ativar MFA (2FA)" />
      <div className="px-screen-x py-6 space-y-5">
        {setup.isPending && <CenterSpinner />}
        {setup.data && (
          <>
            <p className="text-sm text-neutral-700">
              Escaneie o QR no seu app autenticador (Google Authenticator, Authy, 1Password) ou copie o segredo:
            </p>
            <div className="rounded-lg bg-neutral-50 p-4">
              <p className="font-mono break-all text-sm">{setup.data.secret}</p>
            </div>
            <div className="flex justify-center">
              <img
                alt="QR Code MFA"
                className="rounded-lg border border-neutral-200"
                src={`https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(setup.data.otpauth_uri)}`}
              />
            </div>
            <form onSubmit={onVerify} className="space-y-3">
              <div>
                <Label htmlFor="code">Código TOTP (6 dígitos)</Label>
                <Input
                  id="code"
                  inputMode="numeric"
                  pattern="\d{6}"
                  maxLength={6}
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                  className="font-mono tracking-widest text-center"
                />
              </div>
              <Button type="submit" loading={verify.isPending} className="w-full">
                Verificar e ativar
              </Button>
            </form>
          </>
        )}
      </div>
    </MobileFrame>
  );
}
