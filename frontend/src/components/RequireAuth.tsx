import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { CenterSpinner } from '@/components/ui/states';
import { useMe } from '@/hooks/useAuth';
import { useAuthStore } from '@/store/authStore';

interface Props {
  children: ReactNode;
  /** Se true, exige que o usuário tenha uma Conta ativa selecionada. */
  requireConta?: boolean;
}

export function RequireAuth({ children }: Props) {
  const isAuthed = useAuthStore((s) => s.isAuthenticated());
  const location = useLocation();
  if (!isAuthed) {
    return <Navigate to="/auth/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}

/** Exige usuário autenticado COM perfil interno (backoffice). */
export function RequireAdmin({ children }: Props) {
  const isAuthed = useAuthStore((s) => s.isAuthenticated());
  const location = useLocation();
  const { data: me, isLoading } = useMe();

  if (!isAuthed) {
    return <Navigate to="/auth/login" replace state={{ from: location.pathname }} />;
  }
  if (isLoading) {
    return <CenterSpinner />;
  }
  if (!me?.perfil_interno) {
    return <Navigate to="/home" replace />;
  }
  return <>{children}</>;
}
