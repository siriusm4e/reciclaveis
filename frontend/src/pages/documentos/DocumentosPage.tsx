import { Plus, ShieldCheck } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { DocumentAlert } from '@/components/DocumentAlert';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CenterSpinner, EmptyState } from '@/components/ui/states';
import { useDocumentos } from '@/hooks/useDocumentos';
import { formatDate } from '@/utils/dates';

export default function DocumentosPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useDocumentos();

  const venc = data?.filter((d) => d.data_vencimento) ?? [];

  return (
    <AppLayout>
      <TopBar
        title="Documentos"
        action={
          <Button variant="ghost" size="sm" onClick={() => navigate('/documentos/upload')}>
            <Plus className="h-4 w-4" />
          </Button>
        }
      />
      <div className="px-screen-x py-4 space-y-4">
        {venc.length > 0 && (
          <div className="space-y-2">
            {venc.slice(0, 3).map((d) => (
              <DocumentAlert key={d.id} documento={d} />
            ))}
          </div>
        )}

        {isLoading ? (
          <CenterSpinner />
        ) : !data?.length ? (
          <EmptyState
            icon={<ShieldCheck className="h-8 w-8" />}
            titulo="Sem documentos enviados"
            descricao="Para publicar em subcategorias reguladas e participar de oportunidades, anexe os documentos exigidos."
            acao={{ label: 'Enviar documento', onClick: () => navigate('/documentos/upload') }}
          />
        ) : (
          <div className="space-y-2">
            {data.map((d) => (
              <Link key={d.id} to={`/documentos/${d.id}`} className="block">
                <Card className="p-3 hover:bg-neutral-50 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold">Documento</p>
                      {d.numero && <p className="font-mono text-xs">{d.numero}</p>}
                      {d.data_vencimento && (
                        <p className="text-xs text-neutral-500 font-mono">Vence em {formatDate(d.data_vencimento)}</p>
                      )}
                    </div>
                    <StatusBadge status={d.status} />
                  </div>
                  {d.status === 'rejeitado' && d.motivo_rejeicao && (
                    <p className="mt-2 text-xs text-error-dark">{d.motivo_rejeicao}</p>
                  )}
                </Card>
              </Link>
            ))}
          </div>
        )}

        <Link to="/documentos/regularizacao" className="block text-center text-sm text-primary-700 underline">
          Como me regularizar? (MEI, CNAEs)
        </Link>
      </div>
    </AppLayout>
  );
}
