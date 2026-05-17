import { Bell, MapPin } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { useNotificacoesStore } from '@/store/notificacoesStore';

interface Props {
  saudacao: string;
  localizacaoLabel?: string;
  onClickLocalizacao?: () => void;
}

export function GreenHeader({ saudacao, localizacaoLabel, onClickLocalizacao }: Props) {
  const navigate = useNavigate();
  const naoLidas = useNotificacoesStore((s) => s.itens.filter((i) => !i.lida).length);

  return (
    <header className="bg-primary-500 px-screen-x pt-safe pb-4 text-neutral-0">
      <div className="flex items-center justify-between">
        {localizacaoLabel ? (
          <button
            type="button"
            onClick={onClickLocalizacao}
            className="flex items-center gap-1.5 rounded-full bg-white/15 px-3 py-1.5 text-xs font-medium hover:bg-white/25 transition-colors tap-target"
          >
            <MapPin className="h-3.5 w-3.5" />
            <span className="truncate max-w-[160px]">{localizacaoLabel}</span>
          </button>
        ) : (
          <div />
        )}

        <button
          type="button"
          onClick={() => navigate('/notificacoes')}
          className="relative flex h-10 w-10 items-center justify-center rounded-full bg-white/15 hover:bg-white/25 transition-colors"
          aria-label="Notificações"
        >
          <Bell className="h-5 w-5" />
          {naoLidas > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-accent-500 px-1 text-[10px] font-mono font-bold text-neutral-900">
              {naoLidas > 9 ? '9+' : naoLidas}
            </span>
          )}
        </button>
      </div>

      <h2 className="mt-4 text-2xl font-bold tracking-tighter">{saudacao}</h2>
    </header>
  );
}
