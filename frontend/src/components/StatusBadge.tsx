import { Badge, type BadgeProps } from '@/components/ui/badge';
type AnyStatus = string;

const VARIANT_MAP: Record<string, BadgeProps['variant']> = {
  // Negociação
  aberta: 'info',
  combinada: 'primary',
  concluida: 'success',
  cancelada: 'neutral',
  disputada: 'warning',
  expirada: 'neutral',
  // Anúncio
  rascunho: 'neutral',
  publicado: 'success',
  publicada: 'success',
  pausado: 'warning',
  pausada: 'warning',
  expirado: 'neutral',
  arquivado: 'neutral',
  concluido: 'success',
  // Documento
  pendente: 'info',
  aprovado: 'success',
  rejeitado: 'error',
  vencido: 'error',
  // Assinatura/Fatura
  ativa: 'success',
  em_graca: 'warning',
  paga: 'success',
  falha: 'error',
  cortesia: 'primary',
  // Oportunidade
  aberta_para_proposta: 'info',
  encerrada: 'neutral',
  vencedor_declarado: 'success',
  // Proposta
  submetida: 'info',
  vencedora: 'success',
  recusada: 'error',
  // Pedido coleta
  triada: 'info',
  agendada: 'primary',
  coletada: 'success',
  fechada: 'neutral',
  aguardando_municipio: 'warning',
  arquivada_sem_solucao: 'neutral',
  contestada: 'warning',
  // Campanha
  // Denuncia
  em_analise: 'warning',
  resolvida: 'success',
  arquivada: 'neutral',
  // Extra
  urgente: 'error',
};

const LABEL_MAP: Partial<Record<AnyStatus, string>> = {
  aberta_para_proposta: 'ABERTA',
  vencedor_declarado: 'COM VENCEDOR',
  aguardando_municipio: 'AGUARDA MUN.',
  arquivada_sem_solucao: 'SEM SOLUÇÃO',
  em_analise: 'EM ANÁLISE',
  em_graca: 'EM GRAÇA',
};

export function StatusBadge({ status }: { status: AnyStatus }) {
  const variant = VARIANT_MAP[status] ?? 'neutral';
  const label = LABEL_MAP[status] ?? status.replace(/_/g, ' ');
  return <Badge variant={variant}>{label}</Badge>;
}
