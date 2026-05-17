/**
 * Shell do Backoffice — layout responsive Web (sem mobile frame).
 * Sidebar fixa à esquerda em desktop, drawer em mobile.
 */

import {
  BarChart3,
  Bell,
  Briefcase,
  Building2,
  ClipboardList,
  Coins,
  Files,
  Home,
  Megaphone,
  ScrollText,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';

import { cn } from '@/lib/utils';

const ITEMS = [
  { to: '/admin', label: 'Dashboard', icon: Home, end: true },
  { to: '/admin/contas', label: 'Contas', icon: Building2 },
  { to: '/admin/documentos', label: 'Documentos', icon: Files },
  { to: '/admin/catalogo', label: 'Catálogo', icon: ClipboardList },
  { to: '/admin/creditos', label: 'Créditos', icon: Coins },
  { to: '/admin/assinaturas', label: 'Assinaturas', icon: ShieldCheck },
  { to: '/admin/moderacao', label: 'Moderação', icon: Bell },
  { to: '/admin/campanhas', label: 'Campanhas', icon: Megaphone },
  { to: '/admin/conteudo', label: 'Conteúdo', icon: Briefcase },
  { to: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/admin/perfis', label: 'Perfis internos', icon: Users },
  { to: '/admin/audit-log', label: 'Audit log', icon: ScrollText },
] as const;

export default function AdminShell() {
  return (
    <div className="min-h-screen bg-neutral-50 flex">
      <aside className="hidden md:flex w-60 flex-col bg-surface-dark text-neutral-0 sticky top-0 h-screen">
        <div className="px-4 py-5 border-b border-white/10">
          <p className="font-mono text-[10px] tracking-widest text-neutral-400">PNR</p>
          <p className="font-bold tracking-tighter">Backoffice</p>
        </div>
        <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
          {ITEMS.map((it) => {
            const Icon = it.icon;
            return (
              <NavLink
                key={it.to}
                to={it.to}
                end={'end' in it ? it.end : false}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-primary-500 text-neutral-0'
                      : 'text-neutral-300 hover:bg-white/10 hover:text-neutral-0',
                  )
                }
              >
                <Icon className="h-4 w-4" />
                {it.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 min-w-0">
        <header className="md:hidden bg-surface-dark text-neutral-0 px-4 py-3 sticky top-0 z-topbar">
          <p className="font-bold tracking-tighter">PNR · Backoffice</p>
        </header>
        <div className="md:hidden overflow-x-auto px-3 py-2 bg-surface-dark border-t border-white/10 flex gap-1">
          {ITEMS.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              end={'end' in it ? it.end : false}
              className={({ isActive }) =>
                cn(
                  'shrink-0 rounded-full px-3 py-1 text-xs whitespace-nowrap transition-colors',
                  isActive ? 'bg-primary-500 text-neutral-0' : 'bg-white/10 text-neutral-300',
                )
              }
            >
              {it.label}
            </NavLink>
          ))}
        </div>
        <div className="p-4 md:p-8 max-w-screen-xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
