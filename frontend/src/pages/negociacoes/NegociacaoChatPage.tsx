import { Send, MoreVertical } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { MobileFrame } from '@/components/MobileFrame';
import { ChatBubble } from '@/components/ChatBubble';
import { StatusBadge } from '@/components/StatusBadge';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { CenterSpinner, ErrorState } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useContaAtiva } from '@/hooks/useContaAtiva';
import {
  useAcoesNegociacao,
  useEnviarMensagem,
  useLocalizacaoExata,
  useMensagens,
  useNegociacao,
} from '@/hooks/useNegociacao';
import { useChatRealtime } from '@/hooks/useNotificacoes';
import type { MotivoCancelamento } from '@/types/api';

export default function NegociacaoChatPage() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { data: neg, isLoading, error, refetch } = useNegociacao(id);
  const { data: mensagens, refetch: refetchMsg } = useMensagens(id);
  const enviar = useEnviarMensagem(id);
  const acoes = useAcoesNegociacao(id);
  const [conteudo, setConteudo] = useState('');
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [showCancelar, setShowCancelar] = useState(false);
  const [motivo, setMotivo] = useState<MotivoCancelamento>('neutro');
  const [textoCancel, setTextoCancel] = useState('');

  // Realtime
  const onWsEvent = useCallback(() => {
    void refetchMsg();
    void refetch();
  }, [refetch, refetchMsg]);
  useChatRealtime(id, onWsEvent);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [mensagens?.length]);

  // IMPORTANTE: useLocalizacaoExata precisa ser chamado em TODO render (regras de hooks).
  // Cálculos derivados de `neg` ficam seguros com optional chaining; o hook só ativa
  // a query quando podeVerExato=true.
  const aceiteBilateral = Boolean(
    neg?.aceite_localizacao_exata_vendedor && neg?.aceite_localizacao_exata_comprador,
  );
  const podeVerExato = Boolean(
    aceiteBilateral
      && (neg?.status === 'combinada' || neg?.status === 'concluida')
      && neg?.publicacao_tipo === 'anuncio_venda',
  );
  const localExata = useLocalizacaoExata(id, podeVerExato);

  if (isLoading) return <MobileFrame><CenterSpinner /></MobileFrame>;
  if (error || !neg) return <MobileFrame><ErrorState onRetry={refetch} /></MobileFrame>;

  const ehVendedor = conta?.id === neg.conta_vendedora_id;

  const onEnviar = (e: React.FormEvent) => {
    e.preventDefault();
    if (!conteudo.trim()) return;
    enviar.mutate(conteudo.trim(), {
      onSuccess: () => setConteudo(''),
      onError: () => showToast({ title: 'Falha ao enviar', variant: 'error' }),
    });
  };

  const onCancelarConfirm = () => {
    acoes.cancelar.mutate(
      { motivo, texto: textoCancel },
      {
        onSuccess: () => {
          setShowCancelar(false);
          showToast({ title: 'Negociação cancelada', variant: 'info' });
        },
      },
    );
  };

  return (
    <MobileFrame>
      <TopBar
        title={`Negociação`}
        action={<StatusBadge status={neg.status} />}
      />

      <div className="flex flex-col h-[calc(100vh-56px)]">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-screen-x py-3 space-y-2 bg-neutral-50">
          {mensagens?.map((m) => (
            <ChatBubble
              key={m.id}
              conteudo={m.conteudo}
              enviadaPorMim={m.conta_remetente_id === conta?.id}
              ts={m.created_at}
              tipo={m.tipo}
            />
          ))}
          {!mensagens?.length && (
            <p className="py-8 text-center font-serif italic text-sm text-neutral-500">
              Sem mensagens ainda. Apresente-se e proponha os termos.
            </p>
          )}
        </div>

        {/* Painel de ações */}
        {neg.status === 'aberta' && (
          <div className="border-t border-neutral-100 bg-surface-card px-screen-x py-2 space-y-2">
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" className="flex-1" onClick={() => acoes.aceitarLocalizacao.mutate()}>
                {ehVendedor
                  ? neg.aceite_localizacao_exata_vendedor
                    ? 'Localização ✓'
                    : 'Aceitar revelar local'
                  : neg.aceite_localizacao_exata_comprador
                  ? 'Localização ✓'
                  : 'Aceitar revelar local'}
              </Button>
              <Button variant="primary" size="sm" className="flex-1" onClick={() => acoes.confirmar.mutate()}>
                Confirmar combinado
              </Button>
            </div>
          </div>
        )}

        {neg.status === 'combinada' && (
          <div className="border-t border-neutral-100 bg-surface-card px-screen-x py-2 space-y-2">
            {podeVerExato && localExata.data && (
              <p className="text-xs text-neutral-600 font-mono">
                Local exato: {localExata.data.lat.toFixed(6)}, {localExata.data.lng.toFixed(6)}
              </p>
            )}
            <div className="flex gap-2">
              <Button variant="primary" size="sm" className="flex-1" onClick={() => acoes.concluir.mutate()}>
                Marcar como concluída
              </Button>
              <Button variant="ghost" size="sm" onClick={() => navigate(`/negociacoes/${id}/avaliar`)}>
                Avaliar
              </Button>
            </div>
          </div>
        )}

        {neg.status === 'concluida' && (
          <div className="border-t border-neutral-100 bg-success-light px-screen-x py-3 text-center text-sm text-success-dark">
            Negociação concluída.{' '}
            <button onClick={() => navigate(`/negociacoes/${id}/avaliar`)} className="font-semibold underline">
              Avaliar contraparte
            </button>
          </div>
        )}

        {/* Input */}
        {(neg.status === 'aberta' || neg.status === 'combinada' || neg.status === 'disputada') && (
          <form onSubmit={onEnviar} className="border-t border-neutral-100 bg-surface-card px-screen-x py-2 pb-safe flex items-end gap-2">
            <Textarea
              value={conteudo}
              onChange={(e) => setConteudo(e.target.value)}
              placeholder="Mensagem..."
              className="min-h-[44px] max-h-32 flex-1"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  onEnviar(e as unknown as React.FormEvent);
                }
              }}
            />
            <Button type="submit" size="icon" loading={enviar.isPending} aria-label="Enviar">
              <Send className="h-4 w-4" />
            </Button>
            <button
              type="button"
              onClick={() => setShowCancelar(true)}
              className="flex h-tap w-tap items-center justify-center rounded-full text-neutral-500 hover:bg-neutral-100"
              aria-label="Mais ações"
            >
              <MoreVertical className="h-4 w-4" />
            </button>
          </form>
        )}
      </div>

      {/* Cancelar */}
      <Dialog open={showCancelar} onOpenChange={setShowCancelar}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancelar negociação</DialogTitle>
            <DialogDescription>Selecione o motivo. Cancelamentos adversos impactam reputação.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Motivo</Label>
              <Select value={motivo} onValueChange={(v) => setMotivo(v as MotivoCancelamento)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="neutro">Neutro</SelectItem>
                  <SelectItem value="adverso">Adverso (impacta reputação da contraparte)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Detalhe</Label>
              <Input value={textoCancel} onChange={(e) => setTextoCancel(e.target.value)} placeholder="Explique brevemente" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setShowCancelar(false)}>Voltar</Button>
            <Button variant="danger" onClick={onCancelarConfirm} loading={acoes.cancelar.isPending}>Confirmar cancelamento</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </MobileFrame>
  );
}
