import * as React from 'react';
import { AlertTriangle, Inbox, Loader2 } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from './button';

export function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn('h-5 w-5 animate-spin text-primary-500', className)} />;
}

export function CenterSpinner({ label = 'Carregando...' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-neutral-500">
      <Spinner className="h-6 w-6" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('skeleton h-4 w-full rounded-md', className)} />;
}

export function SkeletonList({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="rounded-lg bg-surface-card p-3 shadow-xs">
          <div className="flex gap-3">
            <Skeleton className="h-[72px] w-[72px] rounded-md" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
              <Skeleton className="h-3 w-1/3" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export interface EmptyStateProps {
  titulo: string;
  descricao?: string;
  acao?: { label: string; onClick: () => void };
  icon?: React.ReactNode;
}

export function EmptyState({ titulo, descricao, acao, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-12 text-center">
      <div className="rounded-full bg-primary-50 p-4 text-primary-600">
        {icon ?? <Inbox className="h-8 w-8" />}
      </div>
      <h3 className="text-lg font-bold tracking-tighter text-neutral-900">{titulo}</h3>
      {descricao && <p className="text-sm text-neutral-600 max-w-xs">{descricao}</p>}
      {acao && (
        <Button variant="primary" size="sm" onClick={acao.onClick} className="mt-2">
          {acao.label}
        </Button>
      )}
    </div>
  );
}

export interface ErrorStateProps {
  titulo?: string;
  mensagem?: string;
  onRetry?: () => void;
}

export function ErrorState({
  titulo = 'Algo deu errado',
  mensagem = 'Tente novamente em instantes.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="rounded-xl bg-error-light border border-error/30 p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-error mt-0.5" />
        <div className="flex-1">
          <p className="text-sm font-semibold text-error-dark">{titulo}</p>
          <p className="text-sm text-error-dark/80">{mensagem}</p>
          {onRetry && (
            <Button variant="ghost" size="sm" onClick={onRetry} className="mt-2 text-error-dark">
              Tentar novamente
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
