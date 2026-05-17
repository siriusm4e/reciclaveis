import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { authApi } from '@/api/endpoints/auth';
import { MobileFrame } from '@/components/MobileFrame';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useAuthStore } from '@/store/authStore';

export default function ConvitePage() {
  const { token = '' } = useParams();
  const navigate = useNavigate();
  const isAuthed = useAuthStore((s) => s.isAuthenticated());
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [convite, setConvite] = useState<{ email: string; conta_id: string; status: string; expira_em: string } | null>(null);

  useEffect(() => {
    setLoading(true);
    authApi
      .getConvite(token)
      .then((data) => setConvite(data))
      .catch((e) => setErro(e?.response?.data?.error?.message ?? 'Convite inválido'))
      .finally(() => setLoading(false));
  }, [token]);

  const aceitar = async () => {
    if (!isAuthed) {
      navigate('/auth/login', { state: { from: `/auth/convite/${token}` } });
      return;
    }
    try {
      await authApi.aceitarConvite(token);
      showToast({ title: 'Convite aceito', variant: 'success' });
      navigate('/perfil');
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: { message?: string } } } };
      showToast({ title: 'Falha', description: err.response?.data?.error?.message ?? '', variant: 'error' });
    }
  };

  return (
    <MobileFrame>
      <TopBar title="Convite de equipe" />
      <div className="px-screen-x py-6">
        {loading && <CenterSpinner />}
        {erro && <ErrorState mensagem={erro} />}
        {convite && (
          <div className="space-y-4">
            <p className="text-sm text-neutral-700">
              Você foi convidado(a) para se juntar a uma Conta como Membro.
            </p>
            <div className="rounded-lg bg-surface-card border border-neutral-100 p-4 shadow-xs">
              <p className="text-xs text-neutral-500">E-mail do convite</p>
              <p className="font-mono">{convite.email}</p>
              <p className="mt-2 text-xs text-neutral-500">Status</p>
              <p className="uppercase font-semibold">{convite.status}</p>
            </div>
            <Button onClick={aceitar} disabled={convite.status !== 'pendente'} className="w-full">
              {isAuthed ? 'Aceitar convite' : 'Entrar para aceitar'}
            </Button>
          </div>
        )}
      </div>
    </MobileFrame>
  );
}
