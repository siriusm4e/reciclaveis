import { api } from '@/api/client';
import type { UsuarioPublic } from '@/types/api';

export const usuariosApi = {
  alterarEmail: (senha_atual: string, novo_email: string) =>
    api
      .patch<UsuarioPublic>('/usuarios/me/email', { senha_atual, novo_email })
      .then((r) => r.data),
  alterarSenha: (senha_atual: string, nova_senha: string) =>
    api
      .post('/usuarios/me/senha', { senha_atual, nova_senha })
      .then((r) => r.data),
};
