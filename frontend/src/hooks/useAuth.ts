import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { authApi, type LoginPayload, type RegisterPayload } from '@/api/endpoints/auth';
import { useAuthStore } from '@/store/authStore';
import { useContaStore } from '@/store/contaStore';

export function useMe() {
  const isAuth = useAuthStore((s) => Boolean(s.accessToken));
  return useQuery({
    queryKey: ['me'],
    queryFn: authApi.me,
    enabled: isAuth,
    staleTime: 5 * 60_000,
  });
}

export function useLogin() {
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUsuario = useAuthStore((s) => s.setUsuario);
  const setMfaRequired = useAuthStore((s) => s.setMfaRequired);
  const qc = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (payload: LoginPayload) => authApi.login(payload),
    onSuccess: async (tokens) => {
      setTokens(tokens);
      // Pré-carrega o usuário com o token novo (evita flash na Home/guards).
      // O destino é sempre /home; a Home redireciona superadmin SEM conta para
      // /admin e usuário comum sem conta para /onboarding. Superadmin COM conta
      // (ex.: rodrigo) vê o mapa normalmente e acessa o backoffice pelo menu.
      const me = await qc.fetchQuery({ queryKey: ['me'], queryFn: authApi.me });
      setUsuario(me);
      navigate('/home');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { error?: { details?: { mfa_required?: boolean } } } } };
      if (e.response?.data?.error?.details?.mfa_required) {
        setMfaRequired(true);
      }
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
  });
}

export function useLogout() {
  const { refreshToken, clear } = useAuthStore.getState();
  const clearConta = useContaStore((s) => s.clear);
  const qc = useQueryClient();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async () => {
      if (refreshToken) {
        try {
          await authApi.logout(refreshToken);
        } catch {
          /* segue logout local de qualquer forma */
        }
      }
    },
    onSettled: () => {
      clear();
      clearConta();
      qc.clear();
      navigate('/auth/login');
    },
  });
}

export function useMfaSetup() {
  return useMutation({ mutationFn: authApi.mfaSetup });
}

export function useMfaVerify() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (code: string) => authApi.mfaVerify(code),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['me'] }),
  });
}
