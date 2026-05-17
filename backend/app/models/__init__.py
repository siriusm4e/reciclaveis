"""Registro central de models — chamado por db.base para popular Base.metadata."""

from __future__ import annotations


def register_all_models() -> None:
    """Importa todos os models para que Alembic detecte as tabelas."""
    # Identidade
    from app.models import usuario  # noqa: F401
    from app.models import conta  # noqa: F401
    from app.models import membro  # noqa: F401
    from app.models import papel  # noqa: F401
    from app.models import estabelecimento  # noqa: F401
    from app.models import convite  # noqa: F401

    # Catálogo + documentos
    from app.models import categoria  # noqa: F401
    from app.models import subcategoria  # noqa: F401
    from app.models import atributo_especifico  # noqa: F401
    from app.models import tipo_documento  # noqa: F401
    from app.models import documento  # noqa: F401

    # Marketplace
    from app.models import anuncio_venda  # noqa: F401
    from app.models import oferta_compra  # noqa: F401
    from app.models import anuncio_maquina  # noqa: F401
    from app.models import anuncio_servico  # noqa: F401
    from app.models import anuncio_frete  # noqa: F401
    from app.models import assinatura_alerta  # noqa: F401

    # Negociação / oportunidades
    from app.models import oportunidade  # noqa: F401
    from app.models import proposta  # noqa: F401
    from app.models import negociacao  # noqa: F401
    from app.models import mensagem  # noqa: F401
    from app.models import avaliacao  # noqa: F401
    from app.models import vinculo_detectado  # noqa: F401

    # Créditos / assinaturas
    from app.models import transacao_credito  # noqa: F401
    from app.models import pacote_credito  # noqa: F401
    from app.models import plano  # noqa: F401
    from app.models import assinatura  # noqa: F401
    from app.models import fatura  # noqa: F401
    from app.models import pagamento  # noqa: F401

    # Institucional
    from app.models import pedido_coleta_publica  # noqa: F401
    from app.models import campanha_publica  # noqa: F401

    # Conteúdo / preferências
    from app.models import conteudo_educativo  # noqa: F401
    from app.models import preferencia_comunicacao  # noqa: F401
    from app.models import dispositivo  # noqa: F401

    # Moderação / governança
    from app.models import denuncia  # noqa: F401
    from app.models import decisao_moderacao  # noqa: F401
    from app.models import perfil_interno  # noqa: F401
    from app.models import audit_log  # noqa: F401
