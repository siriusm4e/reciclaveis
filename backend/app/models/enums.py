"""Enums centralizados — nomenclatura canônica (ver REGRAS ABSOLUTAS no spec)."""

from __future__ import annotations

import enum


# === Identidade ===

class ContaTipo(str, enum.Enum):
    PF = "pf"
    PJ_PRIVADA = "pj_privada"
    ORGAO_PUBLICO = "orgao_publico"


class ContaStatus(str, enum.Enum):
    PENDENTE = "pendente"
    EM_REVISAO = "em_revisao"
    ATIVA = "ativa"
    SUSPENSA = "suspensa"
    ANONIMIZADA = "anonimizada"


class PapelInternoMembro(str, enum.Enum):
    """Papel do Membro DENTRO da Conta (não confundir com PapelAtivado)."""

    ADMIN = "admin"
    OPERADOR = "operador"
    LEITOR = "leitor"


class PapelTipo(str, enum.Enum):
    """Papéis que uma Conta pode ativar."""

    CATADOR = "catador"
    COLETOR = "coletor"
    ACUMULADOR = "acumulador"
    COMPRADOR = "comprador"
    GESTOR_RESIDUOS = "gestor_residuos"
    PRESTADOR_SERVICO = "prestador_servico"
    FRETEIRO = "freteiro"  # nunca "Transportador"
    REVENDEDOR_EQUIPAMENTOS = "revendedor_equipamentos"
    GERADOR_INDUSTRIAL = "gerador_industrial"
    PREFEITURA = "prefeitura"
    ORGAO_ESTADUAL = "orgao_estadual"


class PapelStatus(str, enum.Enum):
    PENDENTE = "pendente"
    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"


class ConviteStatus(str, enum.Enum):
    PENDENTE = "pendente"
    ACEITO = "aceito"
    EXPIRADO = "expirado"
    CANCELADO = "cancelado"


# === Documentos ===

class DocumentoStatus(str, enum.Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    VENCIDO = "vencido"


class DocumentoEscopo(str, enum.Enum):
    CONTA = "conta"
    ESTABELECIMENTO = "estabelecimento"


# === Marketplace ===

class AnuncioVendaStatus(str, enum.Enum):
    RASCUNHO = "rascunho"
    PUBLICADO = "publicado"
    PAUSADO = "pausado"
    EXPIRADO = "expirado"
    ARQUIVADO = "arquivado"
    CONCLUIDO = "concluido"


class OfertaCompraStatus(str, enum.Enum):
    RASCUNHO = "rascunho"
    PUBLICADA = "publicada"
    PAUSADA = "pausada"
    EXPIRADA = "expirada"
    CONCLUIDA = "concluida"


class FrequenciaAnuncio(str, enum.Enum):
    LOTE_UNICO = "lote_unico"
    RECORRENTE = "recorrente"


class CondicaoEquipamento(str, enum.Enum):
    NOVO = "novo"
    SEMINOVO = "seminovo"
    USADO = "usado"


class ModalidadeMaquina(str, enum.Enum):
    VENDA = "venda"
    ALUGUEL = "aluguel"
    AMBOS = "ambos"


class UnidadeCobrancaServico(str, enum.Enum):
    HORA = "hora"
    VISITA = "visita"
    LOTE = "lote"


class AnuncioStatus(str, enum.Enum):
    """Status genérico para anúncios de máquina/serviço/frete."""

    RASCUNHO = "rascunho"
    PUBLICADO = "publicado"
    PAUSADO = "pausado"
    EXPIRADO = "expirado"
    ARQUIVADO = "arquivado"


# === Negociação ===

class NegociacaoStatus(str, enum.Enum):
    ABERTA = "aberta"
    COMBINADA = "combinada"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    DISPUTADA = "disputada"
    EXPIRADA = "expirada"


class PublicacaoTipo(str, enum.Enum):
    """Origem da Negociação (publicação que ela negocia)."""

    ANUNCIO_VENDA = "anuncio_venda"
    OFERTA_COMPRA = "oferta_compra"
    OPORTUNIDADE = "oportunidade"
    ANUNCIO_MAQUINA = "anuncio_maquina"
    ANUNCIO_SERVICO = "anuncio_servico"
    ANUNCIO_FRETE = "anuncio_frete"


class MensagemTipo(str, enum.Enum):
    TEXTO = "texto"
    SISTEMA = "sistema"


class MotivoCancelamento(str, enum.Enum):
    NEUTRO = "neutro"
    ADVERSO = "adverso"


# === Oportunidades ===

class OportunidadeTipo(str, enum.Enum):
    LICITACAO = "licitacao"
    CONCORRENCIA = "concorrencia"
    CHAMADA_PUBLICA = "chamada_publica"
    CHAMADA_PRIVADA = "chamada_privada"


class OportunidadeStatus(str, enum.Enum):
    ABERTA_PARA_PROPOSTA = "aberta_para_proposta"
    ENCERRADA = "encerrada"
    CANCELADA = "cancelada"
    VENCEDOR_DECLARADO = "vencedor_declarado"


class PropostaStatus(str, enum.Enum):
    SUBMETIDA = "submetida"
    VENCEDORA = "vencedora"
    RECUSADA = "recusada"
    EXPIRADA = "expirada"


# === Reputação / Vínculo ===

class VinculoMotivo(str, enum.Enum):
    MESMO_CPF_RESPONSAVEL = "mesmo_cpf_responsavel"
    MESMO_TELEFONE = "mesmo_telefone"
    MESMO_CNPJ_RESPONSAVEL = "mesmo_cnpj_responsavel"


# === Créditos / Assinaturas ===

class TransacaoTipo(str, enum.Enum):
    COMPRA = "compra"
    CONSUMO = "consumo"
    REEMBOLSO = "reembolso"
    AJUSTE_ADMIN = "ajuste_admin"
    BONUS = "bonus"


class AssinaturaStatus(str, enum.Enum):
    ATIVA = "ativa"
    EM_GRACA = "em_graca"
    PAUSADA = "pausada"
    CANCELADA = "cancelada"


class FaturaStatus(str, enum.Enum):
    PENDENTE = "pendente"
    PAGA = "paga"
    FALHA = "falha"
    CORTESIA = "cortesia"


class PagamentoMetodo(str, enum.Enum):
    CARTAO = "cartao"
    PIX = "pix"
    BOLETO = "boleto"
    EMPENHO_PUBLICO = "empenho_publico"


class PagamentoStatus(str, enum.Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    FALHA = "falha"


# === Institucional ===

class PedidoColetaStatus(str, enum.Enum):
    ABERTA = "aberta"
    TRIADA = "triada"
    AGENDADA = "agendada"
    COLETADA = "coletada"
    FECHADA = "fechada"
    AGUARDANDO_MUNICIPIO = "aguardando_municipio"
    ARQUIVADA_SEM_SOLUCAO = "arquivada_sem_solucao"
    CONTESTADA = "contestada"


class CampanhaStatus(str, enum.Enum):
    RASCUNHO = "rascunho"
    PUBLICADA = "publicada"
    ENCERRADA = "encerrada"


# === Conteúdo ===

class ConteudoTipo(str, enum.Enum):
    ARTIGO = "artigo"
    DICA = "dica"
    CURSO = "curso"
    VIDEO = "video"


# === Moderação ===

class DenunciaAlvoTipo(str, enum.Enum):
    PUBLICACAO = "publicacao"
    CONTA = "conta"
    MENSAGEM = "mensagem"


class DenunciaTipoFechado(str, enum.Enum):
    CONTEUDO_INAPROPRIADO = "conteudo_inapropriado"
    FRAUDE = "fraude"
    SPAM = "spam"
    ASSEDIO = "assedio"
    OUTRO = "outro"


class DenunciaStatus(str, enum.Enum):
    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    RESOLVIDA = "resolvida"
    ARQUIVADA = "arquivada"


class AcaoModeracao(str, enum.Enum):
    REMOVER = "remover"
    OCULTAR = "ocultar"
    ADVERTIR = "advertir"
    SUSPENDER = "suspender"
    BANIR = "banir"
    ARQUIVAR = "arquivar"


# === Backoffice ===

class PerfilInternoTipo(str, enum.Enum):
    SUPERADMIN = "superadmin"
    OPERADOR_ATENDIMENTO = "operador_atendimento"
    MODERADOR_CONTEUDO = "moderador_conteudo"
    GESTOR_COMERCIAL = "gestor_comercial"
    GESTOR_INSTITUCIONAL = "gestor_institucional"
