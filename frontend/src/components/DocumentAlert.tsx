import { AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';

import { formatDate } from '@/utils/dates';
import type { Documento } from '@/types/api';

interface Props {
  documento: Documento;
  nome?: string;
}

function diasAteVencer(iso: string): number {
  const v = new Date(iso).getTime();
  return Math.ceil((v - Date.now()) / (1000 * 60 * 60 * 24));
}

export function DocumentAlert({ documento, nome }: Props) {
  if (!documento.data_vencimento) return null;
  const dias = diasAteVencer(documento.data_vencimento);
  if (dias > 30 && documento.status !== 'vencido') return null;

  const urgente = dias <= 7 || documento.status === 'vencido';
  const palette = urgente
    ? 'border-l-error bg-error-light text-error-dark'
    : 'border-l-warning bg-warning-light text-warning-dark';

  return (
    <Link
      to={`/documentos/${documento.id}`}
      className={`block border-l-4 ${palette} rounded-md p-3`}
    >
      <div className="flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
        <div className="flex-1 text-sm">
          <p className="font-semibold">
            {documento.status === 'vencido'
              ? `${nome ?? 'Documento'} VENCIDO`
              : `${nome ?? 'Documento'} vence em ${dias}d`}
          </p>
          <p className="opacity-80">
            Vencimento: <span className="font-mono">{formatDate(documento.data_vencimento)}</span>
          </p>
        </div>
      </div>
    </Link>
  );
}
