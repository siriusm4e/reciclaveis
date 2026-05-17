import { Compass, Home, MessageCircle, Plus, User, type LucideIcon } from 'lucide-react';
import { NavLink, useNavigate } from 'react-router-dom';

import { cn } from '@/lib/utils';

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

const ITEMS: NavItem[] = [
  { to: '/home', label: 'Início', icon: Home },
  { to: '/marketplace/buscar', label: 'Buscar', icon: Compass },
  { to: '/negociacoes', label: 'Chats', icon: MessageCircle },
  { to: '/perfil', label: 'Perfil', icon: User },
];

/** Bottom navigation com FAB central (Publicar). */
export function BottomNav() {
  const navigate = useNavigate();
  return (
    <nav
      className="fixed bottom-0 left-1/2 z-tabbar w-full max-w-phone -translate-x-1/2 bg-surface-card shadow-nav-top pb-safe"
      role="navigation"
      aria-label="Navegação principal"
    >
      <div className="grid grid-cols-5 items-end px-2 pt-3 pb-3 relative">
        <Item item={ITEMS[0]} />
        <Item item={ITEMS[1]} />

        <div className="flex justify-center relative -mt-6">
          <button
            type="button"
            onClick={() => navigate('/marketplace/publicar')}
            className="flex h-fab w-fab items-center justify-center rounded-full bg-primary-500 text-neutral-0 shadow-primary transition-transform duration-base hover:bg-primary-600 active:scale-95 tap-target focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
            aria-label="Publicar"
          >
            <Plus className="h-6 w-6" strokeWidth={2.4} />
          </button>
        </div>

        <Item item={ITEMS[2]} />
        <Item item={ITEMS[3]} />
      </div>
    </nav>
  );
}

function Item({ item }: { item: NavItem }) {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.to}
      className={({ isActive }) =>
        cn(
          'flex flex-col items-center gap-1 text-[10px] font-medium uppercase tracking-wider transition-colors',
          isActive ? 'text-primary-500' : 'text-neutral-400 hover:text-neutral-600',
        )
      }
    >
      {({ isActive }) => (
        <>
          <Icon className="h-5 w-5" strokeWidth={isActive ? 2.4 : 2} />
          <span>{item.label}</span>
        </>
      )}
    </NavLink>
  );
}
