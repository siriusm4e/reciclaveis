import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useAtualizarPreferencias, usePreferencias } from '@/hooks/useConteudo';
import { usePushNotifications } from '@/hooks/usePushNotifications';

const ROWS = [
  { key: 'aceita_alerta_pago_de_terceiros', titulo: 'Alertas pagos de terceiros', desc: 'Compradores podem te alertar sobre demandas pagas' },
  { key: 'aceita_comunicacao_prefeitura_municipio', titulo: 'Comunicação da Prefeitura', desc: 'Anúncios da prefeitura do seu município' },
  { key: 'aceita_comunicacao_orgao_estadual', titulo: 'Comunicação do Estado', desc: 'Anúncios do órgão estadual da sua UF' },
  { key: 'aceita_novidades_plataforma', titulo: 'Novidades da plataforma', desc: 'Updates de produto e funcionalidades' },
  { key: 'aceita_conteudo_educativo', titulo: 'Conteúdo educativo', desc: 'Dicas, cursos, vídeos' },
] as const;

export default function PreferenciasPage() {
  const { data, isLoading } = usePreferencias();
  const atualizar = useAtualizarPreferencias();
  const push = usePushNotifications();

  const update = (key: string, value: boolean) => {
    atualizar.mutate(
      { [key]: value },
      {
        onSuccess: () => showToast({ title: 'Preferência atualizada', variant: 'success' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Preferências de comunicação" />
      <div className="px-screen-x py-4 space-y-3">
        <Card className="p-4">
          <h3 className="font-bold tracking-tight mb-1">Notificações push</h3>
          <p className="text-xs text-neutral-500 mb-2">
            Status: <span className="font-mono uppercase">{push.permission}</span>
          </p>
          {push.permission === 'prompt' && (
            <button
              type="button"
              onClick={() => void push.requestPermission()}
              className="text-sm text-primary-700 underline"
            >
              Ativar notificações
            </button>
          )}
          {push.permission === 'denied' && (
            <p className="text-xs text-error-dark">
              Notificações bloqueadas — ajuste nas configurações do navegador.
            </p>
          )}
        </Card>

        {isLoading || !data ? (
          <CenterSpinner />
        ) : (
          ROWS.map((r) => (
            <Card key={r.key} className="flex items-start gap-3 p-3">
              <div className="flex-1">
                <p className="text-sm font-semibold">{r.titulo}</p>
                <p className="text-xs text-neutral-600">{r.desc}</p>
              </div>
              <Switch
                checked={Boolean((data as unknown as Record<string, unknown>)[r.key])}
                onCheckedChange={(v) => update(r.key, v)}
              />
            </Card>
          ))
        )}
        <p className="text-xs text-neutral-500 text-center">
          Mudanças refletem no próximo ciclo de disparo (LGPD by design).
        </p>
      </div>
    </AppLayout>
  );
}
