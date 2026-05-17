import { Bell, Check } from 'lucide-react';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/states';
import { useNotificacoesStore } from '@/store/notificacoesStore';
import { timeAgo } from '@/utils/dates';

export default function NotificacoesPage() {
  const itens = useNotificacoesStore((s) => s.itens);
  const marcarTodas = useNotificacoesStore((s) => s.marcarTodasLidas);
  const marcarLida = useNotificacoesStore((s) => s.marcarLida);

  return (
    <AppLayout>
      <TopBar
        title="Notificações"
        action={
          itens.length > 0 && (
            <Button variant="ghost" size="sm" onClick={marcarTodas}>
              <Check className="h-4 w-4" /> Tudo lido
            </Button>
          )
        }
      />
      <div className="px-screen-x py-4">
        {itens.length === 0 ? (
          <EmptyState
            icon={<Bell className="h-8 w-8" />}
            titulo="Sem notificações"
            descricao="Avisos de novas demandas, alertas pagos e atualizações de negociação aparecem aqui."
          />
        ) : (
          <div className="space-y-2">
            {itens.map((n) => (
              <button
                key={n.id}
                type="button"
                onClick={() => marcarLida(n.id)}
                className={`block w-full rounded-lg border bg-surface-card p-3 text-left transition-colors ${
                  n.lida ? 'border-neutral-100 opacity-70' : 'border-primary-200 shadow-xs'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-semibold text-neutral-900">{n.titulo}</p>
                  <span className="font-mono text-[10px] text-neutral-500">{timeAgo(new Date(n.ts))}</span>
                </div>
                {n.corpo && <p className="mt-1 text-sm text-neutral-700 font-serif italic">{n.corpo}</p>}
              </button>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
