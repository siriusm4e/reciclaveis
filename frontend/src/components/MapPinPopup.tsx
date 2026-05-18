/**
 * Popup contextual exibido ao clicar num pin do MapSearch.
 *
 * A ação principal depende do contexto: quem é a Conta ativa e o tipo da publicação.
 *   - Minha publicação           → "Ver / gerenciar"
 *   - Anúncio de venda alheio    → "Iniciar negociação" (sou potencial comprador)
 *   - Oferta de compra alheia    → "Oferecer material" (sou potencial vendedor)
 */

import { ArrowRight, MapPin, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { showToast } from '@/components/ui/toaster';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import { useAbrirNegociacao } from '@/hooks/useNegociacao';
import { formatBRL } from '@/utils/currency';
import type { ID, PublicacaoTipo } from '@/types/api';

export interface MapPinPopupData {
  /** id da publicação (anúncio ou oferta) */
  publicacao_id: ID;
  /** "venda" ou "compra" */
  tipo: 'venda' | 'compra';
  titulo: string;
  preco?: string | number | null;
  unidade?: string | null;
  /** conta dona da publicação — usado pra detectar "minha publicação" */
  conta_id?: ID;
  /** descrição curta (até ~120 chars idealmente) */
  descricao?: string | null;
  /** volume / quantidade exibida ao lado da unidade */
  volume?: string | number | null;
  /** flags extras */
  boost_ativo?: boolean;
  /** raio do comprador (apenas para tipo=compra) */
  raio_km?: number | null;
  /** comprador retira no local do vendedor (tipo=compra) */
  retira?: boolean;
}

export function MapPinPopup({ data }: { data: MapPinPopupData }) {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const abrirNeg = useAbrirNegociacao();

  const ehMinhaPublicacao = Boolean(conta && data.conta_id && conta.id === data.conta_id);
  const linkDetalhe =
    data.tipo === 'venda' ? `/anuncios/${data.publicacao_id}` : `/ofertas/${data.publicacao_id}`;

  const onNegociar = () => {
    const publicacao_tipo: PublicacaoTipo =
      data.tipo === 'venda' ? 'anuncio_venda' : 'oferta_compra';
    abrirNeg.mutate(
      { publicacao_id: data.publicacao_id, publicacao_tipo },
      {
        onSuccess: (neg) => navigate(`/negociacoes/${neg.id}`),
        onError: (err) =>
          showToast({
            title: 'Falha ao iniciar negociação',
            description: extractErrorMessage(err),
            variant: 'error',
          }),
      },
    );
  };

  return (
    <div className="font-sans" style={{ minWidth: 220, maxWidth: 280 }}>
      <div className="flex items-center justify-between gap-2 mb-2">
        <Badge variant={data.tipo === 'venda' ? 'primary' : 'accent'}>
          {data.tipo === 'venda' ? 'À VENDA' : 'COMPRA'}
        </Badge>
        {data.boost_ativo && (
          <span className="inline-flex items-center gap-0.5 text-[10px] font-bold uppercase tracking-wider text-accent-600">
            <Sparkles className="h-3 w-3" /> Boost
          </span>
        )}
      </div>

      <h3 className="text-sm font-bold tracking-tight text-neutral-900 leading-snug line-clamp-2 mb-1.5">
        {data.titulo}
      </h3>

      <div className="flex items-baseline gap-1 mb-1">
        <span
          className={`font-mono font-bold text-lg leading-tight ${
            data.tipo === 'venda' ? 'text-primary-700' : 'text-accent-600'
          }`}
        >
          {formatBRL(data.preco)}
        </span>
        {data.unidade && <span className="text-xs text-neutral-500">/{data.unidade}</span>}
      </div>

      {data.tipo === 'compra' && (data.raio_km || data.retira) && (
        <p className="text-xs text-neutral-600 mb-1">
          {data.retira ? 'Comprador retira ' : 'Entregar em '}
          até <span className="font-mono">{data.raio_km}km</span>
        </p>
      )}

      {data.descricao && (
        <p className="text-xs text-neutral-600 line-clamp-2 mb-2 font-serif italic">
          {data.descricao}
        </p>
      )}

      {data.tipo === 'venda' && (
        <p className="flex items-start gap-1 text-[10px] text-neutral-500 mb-2">
          <MapPin className="h-3 w-3 mt-0.5 shrink-0" />
          <span>Localização aproximada (privacidade do vendedor).</span>
        </p>
      )}

      <div className="flex flex-col gap-1.5 mt-2">
        {ehMinhaPublicacao ? (
          <>
            <Badge variant="info" className="self-start">SUA PUBLICAÇÃO</Badge>
            <Button
              size="sm"
              variant="primary"
              onClick={() => navigate(linkDetalhe)}
              className="w-full"
            >
              Ver / gerenciar <ArrowRight className="h-3.5 w-3.5" />
            </Button>
            {data.tipo === 'compra' && (
              <Button
                size="sm"
                variant="accent"
                onClick={() => navigate(`/ofertas/${data.publicacao_id}/alerta-pago`)}
                className="w-full"
              >
                <Sparkles className="h-3.5 w-3.5" /> Configurar Alerta Pago
              </Button>
            )}
          </>
        ) : (
          <>
            <Button
              size="sm"
              variant={data.tipo === 'venda' ? 'primary' : 'accent'}
              onClick={onNegociar}
              loading={abrirNeg.isPending}
              className="w-full"
            >
              {data.tipo === 'venda' ? 'Iniciar negociação' : 'Oferecer material'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => navigate(linkDetalhe)}
              className="w-full"
            >
              Ver detalhes <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
