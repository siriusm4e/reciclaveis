import { MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

import { cn } from '@/lib/utils';
import { formatBRL } from '@/utils/currency';
import { timeAgo } from '@/utils/dates';

export interface ListingCardProps {
  to: string;
  titulo: string;
  preco: number | string | null;
  unidade?: string | null;
  cidade?: string | null;
  uf?: string | null;
  tipo: 'venda' | 'compra' | 'maquina' | 'servico' | 'frete';
  destaque?: boolean;
  fotoUrl?: string | null;
  createdAt?: string | null;
}

const TIPO_LABEL: Record<ListingCardProps['tipo'], string> = {
  venda: 'À VENDA',
  compra: 'COMPRA',
  maquina: 'EQUIPAMENTO',
  servico: 'SERVIÇO',
  frete: 'FRETE',
};

export function ListingCard({
  to,
  titulo,
  preco,
  unidade,
  cidade,
  uf,
  tipo,
  destaque = false,
  fotoUrl,
  createdAt,
}: ListingCardProps) {
  // Verde para venda, Âmbar para compra (Design System)
  const accentSide = tipo === 'venda' ? 'bg-primary-500' : tipo === 'compra' ? 'bg-accent-500' : 'bg-neutral-300';

  return (
    <Link
      to={to}
      className={cn(
        'relative block overflow-hidden rounded-lg bg-surface-card p-3 shadow-xs border border-neutral-100',
        'transition-shadow duration-base hover:shadow-sm',
        destaque && 'border-accent-500/30 shadow-accent',
      )}
    >
      {destaque && (
        <span className="absolute -top-1.5 left-3 z-10 rounded-sm bg-accent-500 px-2 py-0.5 text-[9px] font-bold tracking-wider text-neutral-900 shadow-sm">
          DESTAQUE
        </span>
      )}
      <span className={cn('absolute left-0 top-0 bottom-0 w-[3px]', accentSide)} />
      <div className="flex gap-3 pl-1">
        <div className="h-[72px] w-[72px] flex-shrink-0 overflow-hidden rounded-md bg-gradient-to-br from-primary-100 to-primary-300">
          {fotoUrl && (
            <img src={fotoUrl} alt={titulo} className="h-full w-full object-cover" loading="lazy" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-neutral-500">
            <span>{TIPO_LABEL[tipo]}</span>
            {createdAt && <span className="text-neutral-400">· {timeAgo(createdAt)}</span>}
          </div>
          <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-neutral-800 tracking-tight">
            {titulo}
          </h3>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="font-mono text-base font-bold text-primary-700">{formatBRL(preco)}</span>
            {unidade && <span className="text-xs text-neutral-500">/{unidade}</span>}
          </div>
          {(cidade || uf) && (
            <div className="mt-1 flex items-center gap-1 text-xs text-neutral-500">
              <MapPin className="h-3 w-3" />
              <span>
                {cidade}
                {uf ? ` · ${uf}` : ''}
              </span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
