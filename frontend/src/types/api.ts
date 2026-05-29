/**
 * Types TS espelhando os schemas Pydantic do backend.
 * Mantidos manualmente — em projeto maior considere openapi-typescript-codegen.
 */

// ===== Enums =====

export type ContaTipo = 'pf' | 'pj_privada' | 'orgao_publico';
export type ContaStatus = 'pendente' | 'em_revisao' | 'ativa' | 'suspensa' | 'anonimizada';
export type PapelInternoMembro = 'admin' | 'operador' | 'leitor';

export type PapelTipo =
  | 'catador'
  | 'coletor'
  | 'acumulador'
  | 'comprador'
  | 'gestor_residuos'
  | 'prestador_servico'
  | 'freteiro'
  | 'revendedor_equipamentos'
  | 'gerador_industrial'
  | 'prefeitura'
  | 'orgao_estadual';

export type PapelStatus = 'pendente' | 'ativo' | 'bloqueado';
export type ConviteStatus = 'pendente' | 'aceito' | 'expirado' | 'cancelado';

export type DocumentoStatus = 'pendente' | 'aprovado' | 'rejeitado' | 'vencido';
export type DocumentoEscopo = 'conta' | 'estabelecimento';

export type AnuncioVendaStatus =
  | 'rascunho'
  | 'publicado'
  | 'pausado'
  | 'expirado'
  | 'arquivado'
  | 'concluido';

export type OfertaCompraStatus =
  | 'rascunho'
  | 'publicada'
  | 'pausada'
  | 'expirada'
  | 'concluida';

export type FrequenciaAnuncio = 'lote_unico' | 'recorrente';

// Condição (grupos exclusivos no formulário/filtro)
export type CondicaoLimpeza = 'limpo' | 'sujo' | 'contaminado';
export type CondicaoUmidade = 'seco' | 'umido' | 'molhado';
export type CondicaoForma =
  | 'solto'
  | 'fardo'
  | 'prensado'
  | 'moido'
  | 'triturado'
  | 'granulado';
export type CondicaoEquipamento = 'novo' | 'seminovo' | 'usado';
export type ModalidadeMaquina = 'venda' | 'aluguel' | 'ambos';
export type UnidadeCobrancaServico = 'hora' | 'visita' | 'lote';
export type AnuncioStatus = 'rascunho' | 'publicado' | 'pausado' | 'expirado' | 'arquivado';

export type NegociacaoStatus =
  | 'aberta'
  | 'combinada'
  | 'concluida'
  | 'cancelada'
  | 'disputada'
  | 'expirada';

export type PublicacaoTipo =
  | 'anuncio_venda'
  | 'oferta_compra'
  | 'oportunidade'
  | 'anuncio_maquina'
  | 'anuncio_servico'
  | 'anuncio_frete';

export type MensagemTipo = 'texto' | 'sistema';
export type MotivoCancelamento = 'neutro' | 'adverso';

export type OportunidadeTipo = 'licitacao' | 'concorrencia' | 'chamada_publica' | 'chamada_privada';
export type OportunidadeStatus =
  | 'aberta_para_proposta'
  | 'encerrada'
  | 'cancelada'
  | 'vencedor_declarado';
export type PropostaStatus = 'submetida' | 'vencedora' | 'recusada' | 'expirada';

export type TransacaoTipo = 'compra' | 'consumo' | 'reembolso' | 'ajuste_admin' | 'bonus';
export type AssinaturaStatus = 'ativa' | 'em_graca' | 'pausada' | 'cancelada';
export type FaturaStatus = 'pendente' | 'paga' | 'falha' | 'cortesia';
export type PagamentoMetodo = 'cartao' | 'pix' | 'boleto' | 'empenho_publico';
export type PagamentoStatus = 'pendente' | 'aprovado' | 'falha';

export type PedidoColetaStatus =
  | 'aberta'
  | 'triada'
  | 'agendada'
  | 'coletada'
  | 'fechada'
  | 'aguardando_municipio'
  | 'arquivada_sem_solucao'
  | 'contestada';

export type CampanhaStatus = 'rascunho' | 'publicada' | 'encerrada';
export type ConteudoTipo = 'artigo' | 'dica' | 'curso' | 'video';

export type DenunciaAlvoTipo = 'publicacao' | 'conta' | 'mensagem';
export type DenunciaTipoFechado =
  | 'conteudo_inapropriado'
  | 'fraude'
  | 'spam'
  | 'assedio'
  | 'outro';
export type DenunciaStatus = 'aberta' | 'em_analise' | 'resolvida' | 'arquivada';
export type AcaoModeracao =
  | 'remover'
  | 'ocultar'
  | 'advertir'
  | 'suspender'
  | 'banir'
  | 'arquivar';

export type PerfilInternoTipo =
  | 'superadmin'
  | 'operador_atendimento'
  | 'moderador_conteudo'
  | 'gestor_comercial'
  | 'gestor_institucional';

// ===== Entities =====

export interface UUID {
  /** UUID v4 string */
}
export type ID = string;

export interface PerfilInternoPublic {
  tipo: PerfilInternoTipo;
  ativo: boolean;
}

export interface UsuarioPublic {
  id: ID;
  email: string;
  nome_completo: string;
  telefone: string | null;
  foto_path: string | null;
  mfa_ativo: boolean;
  email_confirmado: boolean;
  ativo: boolean;
  created_at: string;
  perfil_interno: PerfilInternoPublic | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface Conta {
  id: ID;
  created_at: string;
  updated_at: string;
  tipo: ContaTipo;
  status: ContaStatus;
  nome_publico: string;
  cnpj: string | null;
  foto_perfil_path: string | null;
  escopo_territorial: Record<string, unknown> | null;
  cortesia_ativa: boolean;
}

export interface Membro {
  id: ID;
  usuario_id: ID;
  conta_id: ID;
  papel_interno: PapelInternoMembro;
  created_at: string;
  updated_at: string;
}

export interface Papel {
  id: ID;
  conta_id: ID;
  papel: PapelTipo;
  status: PapelStatus;
  dados_complementares: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Estabelecimento {
  id: ID;
  conta_id: ID;
  nome: string;
  cep: string;
  logradouro: string;
  numero: string;
  complemento: string | null;
  bairro: string;
  cidade: string;
  uf: string;
  ibge_municipio: string | null;
  lat: number;
  lng: number;
  created_at: string;
  updated_at: string;
}

export interface Categoria {
  id: ID;
  nome: string;
  slug: string;
  cor_hex: string;
  icone: string;
  ordem: number;
  ativo: boolean;
}

/**
 * Subcategoria — nível intermediário (Categoria → Subcategoria → TipoMaterial).
 * Regulação documental vive aqui; unidade_padrao + atributos vivem em TipoMaterial.
 */
export interface Subcategoria {
  id: ID;
  categoria_id: ID;
  nome: string;
  slug: string;
  requer_validacao_documental: boolean;
  documentos_exigidos: string[];
  ordem: number;
  ativo: boolean;
}

/**
 * TipoMaterial — nível mais granular (PET cristal, Alumínio latinha, ...).
 */
export interface TipoMaterial {
  id: ID;
  subcategoria_id: ID;
  nome: string;
  slug: string;
  unidade_padrao: string;
  atributos_especificos: Record<string, unknown>;
  ordem: number;
  ativo: boolean;
}

export interface TipoDocumento {
  id: ID;
  slug: string;
  nome: string;
  descricao: string | null;
  escopo: DocumentoEscopo;
  papeis_aplicaveis: string[];
  tem_vencimento: boolean;
  exige_aprovacao_manual: boolean;
  obrigatorio: boolean;
  ativo: boolean;
}

export interface Documento {
  id: ID;
  conta_id: ID;
  estabelecimento_id: ID | null;
  tipo_documento_id: ID;
  numero: string | null;
  data_emissao: string | null;
  data_vencimento: string | null;
  arquivo_path: string;
  mime: string;
  tamanho_bytes: number;
  status: DocumentoStatus;
  substitui_id: ID | null;
  motivo_rejeicao: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnuncioVenda {
  id: ID;
  conta_id: ID;
  papel_id: ID;
  tipo_material_id: ID;
  atributos: Record<string, unknown>;
  // Condição (grupos exclusivos)
  condicao_limpeza: CondicaoLimpeza | null;
  condicao_umidade: CondicaoUmidade | null;
  condicao_forma: CondicaoForma | null;
  lat_pub: number;
  lng_pub: number;
  offset_m: number;
  territorio: string;
  preco_pretendido: string;
  unidade: string;
  volume_estimado: string | null;
  frequencia: FrequenciaAnuncio;
  intervalo_geracao: string | null;
  prazo_validade: string;
  status: AnuncioVendaStatus;
  fotos: string[];
  aceita_alerta_pago_de_terceiros: boolean;
  visualizacoes: number;
  created_at: string;
  updated_at: string;
}

export interface OfertaCompra {
  id: ID;
  conta_id: ID;
  papel_id: ID;
  tipo_material_id: ID;
  titulo: string;
  descricao: string | null;
  especificacao: Record<string, unknown>;
  preco_paga: string;
  unidade: string;
  volume_min: string;
  volume_max: string | null;
  // Filtro mútuo: vendedor só vê esta oferta se volume_estimado ≥ volume_minimo_kg
  volume_minimo_kg: number | null;
  condicao_limpeza: CondicaoLimpeza | null;
  condicao_umidade: CondicaoUmidade | null;
  condicao_forma: CondicaoForma | null;
  lat: number;
  lng: number;
  raio_km: number;
  retira: boolean;
  prazo_validade: string;
  status: OfertaCompraStatus;
  boost_ativo: boolean;
  boost_raio_km: number | null;
  boost_duracao_horas: number | null;
  boost_inicio: string | null;
  boost_fim: string | null;
  created_at: string;
  updated_at: string;
}

export interface Negociacao {
  id: ID;
  publicacao_id: ID;
  publicacao_tipo: PublicacaoTipo;
  conta_vendedora_id: ID;
  conta_compradora_id: ID;
  status: NegociacaoStatus;
  aceite_localizacao_exata_vendedor: boolean;
  aceite_localizacao_exata_comprador: boolean;
  combinada_em: string | null;
  motivo_cancelamento: MotivoCancelamento | null;
  motivo_cancelamento_texto: string | null;
  ultima_mensagem_em: string | null;
  ultima_mensagem_preview: string | null;
  created_at: string;
  updated_at: string;
}

export interface Mensagem {
  id: ID;
  negociacao_id: ID;
  conta_remetente_id: ID;
  usuario_remetente_id: ID | null;
  conteudo: string;
  tipo: MensagemTipo;
  created_at: string;
  updated_at: string;
}

export interface Avaliacao {
  id: ID;
  negociacao_id: ID;
  avaliador_conta_id: ID;
  avaliado_conta_id: ID;
  papel_avaliado: PapelTipo;
  nota: number;
  subnotas: Record<string, unknown>;
  comentario: string | null;
  visivel: boolean;
  removida: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReputacaoConta {
  conta_id: ID;
  por_papel: Array<{ papel: PapelTipo; media: number; total_avaliacoes: number }>;
}

export interface SaldoCreditos {
  conta_id: ID;
  saldo: number;
}

export interface TransacaoCredito {
  id: ID;
  conta_id: ID;
  tipo: TransacaoTipo;
  valor: number;
  descricao: string;
  referencia_tipo: string | null;
  referencia_id: ID | null;
  admin_id: ID | null;
  created_at: string;
  updated_at: string;
}

export interface PacoteCredito {
  id: ID;
  nome: string;
  descricao: string | null;
  creditos: number;
  bonus: number;
  preco_centavos: number;
  ordem: number;
  ativo: boolean;
}

export interface Plano {
  id: ID;
  papel: PapelTipo;
  nome: string;
  descricao: string | null;
  limite_publicacoes_ativas: number;
  permite_alerta_pago: boolean;
  preco_mensal_centavos: number;
  gratuito: boolean;
  ativo: boolean;
}

export interface Assinatura {
  id: ID;
  conta_id: ID;
  papel_id: ID;
  plano_id: ID;
  status: AssinaturaStatus;
  data_inicio: string;
  data_renovacao: string;
  em_graca_desde: string | null;
  pausada_desde: string | null;
  cancelada_em: string | null;
  ciclo_cortesia: boolean;
  created_at: string;
  updated_at: string;
}

export interface Fatura {
  id: ID;
  assinatura_id: ID;
  ciclo_inicio: string;
  ciclo_fim: string;
  valor_centavos: number;
  status: FaturaStatus;
  vencimento: string;
  created_at: string;
  updated_at: string;
}

export interface Oportunidade {
  id: ID;
  conta_id: ID;
  titulo: string;
  descricao: string;
  subcategoria_id: ID;
  tipo: OportunidadeTipo;
  documentos_exigidos: string[];
  prazo_submissao: string;
  valor_estimado: string | null;
  status: OportunidadeStatus;
  proposta_vencedora_id: ID | null;
  created_at: string;
  updated_at: string;
}

export interface Proposta {
  id: ID;
  oportunidade_id: ID;
  conta_proponente_id: ID;
  valor: string;
  condicoes: string | null;
  documentos_anexos: string[];
  status: PropostaStatus;
  created_at: string;
  updated_at: string;
}

export interface AnuncioMaquina {
  id: ID;
  conta_id: ID;
  papel_id: ID | null;
  categoria_equipamento: string;
  marca: string | null;
  modelo: string | null;
  ano: number | null;
  capacidade: string | null;
  tensao: string | null;
  descricao: string | null;
  condicao: CondicaoEquipamento;
  modalidade: ModalidadeMaquina;
  aceita_visita_tecnica: boolean;
  disponibilidade: Record<string, unknown> | null;
  preco: string;
  documentacao_disponivel: boolean;
  fotos: string[];
  lat: number;
  lng: number;
  prazo_validade: string;
  status: AnuncioStatus;
  created_at: string;
  updated_at: string;
}

export interface AnuncioServico {
  id: ID;
  conta_id: ID;
  papel_id: ID;
  tipo_servico: string;
  descricao: string | null;
  raio_operacional_km: number;
  unidade_cobranca: UnidadeCobrancaServico;
  preco: string | null;
  requer_visita_tecnica: boolean;
  disponibilidade: Record<string, unknown> | null;
  lat: number;
  lng: number;
  prazo_validade: string;
  status: AnuncioStatus;
  created_at: string;
  updated_at: string;
}

export interface AnuncioFrete {
  id: ID;
  conta_id: ID;
  papel_id: ID;
  tipo_veiculo: string;
  capacidade_t: string | null;
  capacidade_m3: string | null;
  tara: string | null;
  raio_operacional_km: number;
  categorias_residuo_aceitas: string[];
  licencas: string[];
  emite_nf: boolean;
  lat: number;
  lng: number;
  prazo_validade: string;
  status: AnuncioStatus;
  created_at: string;
  updated_at: string;
}

export interface PedidoColeta {
  id: ID;
  conta_solicitante_id: ID;
  prefeitura_conta_id: ID | null;
  bairro: string;
  cidade: string;
  uf: string;
  ibge_municipio: string | null;
  tipo_residuo: string;
  foto_path: string | null;
  quantidade_estimada: string | null;
  descricao: string | null;
  lat: number;
  lng: number;
  status: PedidoColetaStatus;
  created_at: string;
  updated_at: string;
}

export interface Campanha {
  id: ID;
  conta_organizadora_id: ID;
  titulo: string;
  descricao: string;
  data_evento: string | null;
  tipo_residuo: string | null;
  beneficio: string | null;
  cidade: string | null;
  uf: string | null;
  ibge_municipio: string | null;
  status: CampanhaStatus;
  created_at: string;
  updated_at: string;
}

export interface ConteudoEducativo {
  id: ID;
  titulo: string;
  resumo: string | null;
  tipo: ConteudoTipo;
  papeis_alvo: string[];
  categorias_alvo: string[];
  url: string | null;
  conteudo: string | null;
  capa_path: string | null;
  publicado: boolean;
  created_at: string;
  updated_at: string;
}

export interface PreferenciaComunicacao {
  id: ID;
  conta_id: ID;
  aceita_alerta_pago_de_terceiros: boolean;
  aceita_comunicacao_prefeitura_municipio: boolean;
  aceita_comunicacao_orgao_estadual: boolean;
  aceita_novidades_plataforma: boolean;
  aceita_conteudo_educativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Denuncia {
  id: ID;
  denunciante_conta_id: ID;
  alvo_tipo: DenunciaAlvoTipo;
  alvo_id: ID;
  tipo_fechado: DenunciaTipoFechado;
  descricao: string;
  status: DenunciaStatus;
  created_at: string;
  updated_at: string;
}

export interface AlertaPagoConfig {
  raio_km: number;
  duracao_horas: number;
  segmentacao: Record<string, unknown>;
}

export interface AlertaPagoResultado {
  cobertura: number;
  cobertura_minima: number;
  disparou: boolean;
  creditos_debitados: number;
  creditos_reembolsados: number;
  oferta_id: ID;
}

// ===== API error envelope =====

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}
