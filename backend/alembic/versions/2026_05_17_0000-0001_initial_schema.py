"""Initial schema — PostGIS + todas as 36 tabelas com índices GIST e enums.

Revision ID: 0001
Revises:
Create Date: 2026-05-17 00:00:00

Estratégia: migration baseline. Habilita a extensão PostGIS e cria todas as
tabelas a partir de `Base.metadata` (que já agrupa todos os models registrados).
Vantagens:
  - Fidelidade absoluta aos models (sem divergência manual)
  - Geoalchemy2 cria índices GIST automaticamente em colunas Geometry
  - Enums Postgres criados pelo SQLAlchemy a partir dos SAEnum nos models

Limitação conhecida: autogenerate de migrations futuras pode reportar diffs
falsos para enums e índices criados implicitamente. Tratar caso a caso.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.db.base import Base  # importa Base + registra todos os models

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. PostGIS — obrigatório antes de qualquer coluna Geometry
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Cria todas as tabelas + enums + índices (inclusive GIST) conforme metadata
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()

    # Remove tabelas em ordem reversa de dependências
    Base.metadata.drop_all(bind=bind)

    # Drop enums Postgres criados pelo SQLAlchemy
    enum_names = [
        "conta_tipo",
        "conta_status",
        "papel_interno_membro",
        "papel_tipo",
        "papel_status",
        "convite_status",
        "documento_status",
        "documento_escopo",
        "anuncio_venda_status",
        "oferta_compra_status",
        "frequencia_anuncio",
        "condicao_equipamento",
        "modalidade_maquina",
        "unidade_cobranca_servico",
        "anuncio_status",
        "negociacao_status",
        "publicacao_tipo",
        "mensagem_tipo",
        "motivo_cancelamento",
        "oportunidade_tipo",
        "oportunidade_status",
        "proposta_status",
        "vinculo_motivo",
        "transacao_tipo",
        "assinatura_status",
        "fatura_status",
        "pagamento_metodo",
        "pagamento_status",
        "pedido_coleta_status",
        "campanha_status",
        "conteudo_tipo",
        "denuncia_alvo_tipo",
        "denuncia_tipo_fechado",
        "denuncia_status",
        "acao_moderacao",
        "perfil_interno_tipo",
    ]
    for name in enum_names:
        op.execute(f"DROP TYPE IF EXISTS {name} CASCADE;")

    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE;")
