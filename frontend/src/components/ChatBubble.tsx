import { cn } from '@/lib/utils';
import { timeAgo } from '@/utils/dates';

interface Props {
  conteudo: string;
  enviadaPorMim: boolean;
  ts: string;
  tipo: 'texto' | 'sistema';
  remetenteLabel?: string;
}

/** Bolha de chat — Source Serif 4 italic para mensagens humanas. */
export function ChatBubble({ conteudo, enviadaPorMim, ts, tipo, remetenteLabel }: Props) {
  if (tipo === 'sistema') {
    return (
      <div className="my-2 flex justify-center">
        <span className="rounded-full bg-neutral-100 px-3 py-1 text-xs text-neutral-600">
          {conteudo}
        </span>
      </div>
    );
  }

  return (
    <div className={cn('flex', enviadaPorMim ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-3.5 py-2.5 shadow-xs',
          enviadaPorMim
            ? 'rounded-br-md bg-primary-500 text-neutral-0'
            : 'rounded-bl-md bg-surface-card text-neutral-900',
        )}
      >
        {!enviadaPorMim && remetenteLabel && (
          <p className="mb-0.5 text-xs font-semibold text-primary-700">{remetenteLabel}</p>
        )}
        <p className="font-serif italic text-base leading-relaxed">{conteudo}</p>
        <p
          className={cn(
            'mt-1 text-right text-[10px]',
            enviadaPorMim ? 'text-primary-100' : 'text-neutral-400',
          )}
        >
          {timeAgo(ts)}
        </p>
      </div>
    </div>
  );
}
