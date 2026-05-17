import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

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
