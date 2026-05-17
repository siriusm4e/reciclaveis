import {
  Award,
  Building2,
  ChevronRight,
  FileText,
  LogOut,
  Plus,
  Settings,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { CreditBalance } from '@/components/CreditBalance';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useMe, useLogout } from '@/hooks/useAuth';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { maskCNPJ } from '@/utils/currency';

export default function PerfilPage() {
  const navigate = useNavigate();
  const { data: me } = useMe();
  const conta = useContaAtiva();
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const logout = useLogout();

  return (
    <AppLayout>
      <TopBar title="Perfil" back={false} />
      <div className="px-screen-x py-4 space-y-4">
        <Card className="p-4">
          <div className="flex items-start gap-3">
            <div className="h-14 w-14 rounded-full bg-primary-100 text-primary-700 font-bold text-xl flex items-center justify-center">
              {conta?.nome_publico.charAt(0).toUpperCase() ?? me?.nome_completo.charAt(0)}
            </div>
            <div className="flex-1">
              <h2 className="font-bold tracking-tight">{conta?.nome_publico ?? '—'}</h2>
              <p className="text-xs text-neutral-500 uppercase tracking-wider">{conta?.tipo.replace('_', ' ')}</p>
              {conta?.cnpj && <p className="font-mono text-xs">{maskCNPJ(conta.cnpj)}</p>}
              <p className="text-xs text-neutral-500 mt-1">{me?.email}</p>
            </div>
            <Link to="/perfil/trocar-conta" className="text-primary-700 text-xs underline">
              Trocar
            </Link>
          </div>
        </Card>

        <CreditBalance />

        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-bold tracking-tight">Papéis ativos</h3>
            <Button variant="ghost" size="sm" onClick={() => navigate('/perfil/papeis/novo')}>
              <Plus className="h-4 w-4" /> Ativar
            </Button>
          </div>
          {!papeis?.length ? (
            <p className="text-sm text-neutral-500">Nenhum papel ativo ainda.</p>
          ) : (
            <div className="space-y-2">
              {papeis.map((p) => (
                <Link key={p.id} to={`/perfil/papeis/${p.id}`} className="block">
                  <Card className="flex items-center justify-between p-3 hover:bg-neutral-50 transition-colors">
                    <span className="capitalize text-sm font-semibold">{p.papel.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={p.status === 'ativo' ? 'aprovado' : p.status === 'pendente' ? 'pendente' : 'cancelada'} />
                      <ChevronRight className="h-4 w-4 text-neutral-400" />
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>

        <nav className="space-y-1.5">
          <PerfilLink to="/perfil/reputacao" icon={<Award className="h-4 w-4" />} label="Reputação" />
          <PerfilLink to="/perfil/membros" icon={<Users className="h-4 w-4" />} label="Membros e convites" />
          <PerfilLink to="/documentos" icon={<FileText className="h-4 w-4" />} label="Documentos" />
          <PerfilLink to="/assinaturas" icon={<ShieldCheck className="h-4 w-4" />} label="Plano e faturas" />
          <PerfilLink to="/configuracoes/preferencias" icon={<Settings className="h-4 w-4" />} label="Preferências de comunicação" />
          <PerfilLink to="/admin" icon={<Building2 className="h-4 w-4" />} label="Backoffice (interno)" />
        </nav>

        <Button variant="ghost" className="w-full text-error" onClick={() => logout.mutate()}>
          <LogOut className="h-4 w-4" /> Sair
        </Button>
      </div>
    </AppLayout>
  );
}

function PerfilLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <Link
      to={to}
      className="flex items-center justify-between rounded-lg bg-surface-card border border-neutral-100 p-3 text-sm text-neutral-800 hover:bg-neutral-50 transition-colors"
    >
      <span className="inline-flex items-center gap-2.5">
        <span className="text-primary-600">{icon}</span>
        {label}
      </span>
      <ChevronRight className="h-4 w-4 text-neutral-400" />
    </Link>
  );
}
