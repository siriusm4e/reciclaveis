"""Condição (3 grupos exclusivos) + volume mínimo de oferta + drop titulo/descricao do anúncio.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-18 01:00:00

Mudanças:
  - Cria enums Postgres: condicao_limpeza, condicao_umidade, condicao_forma.
  - anuncio_venda: drop colunas `titulo` (NOT NULL) e `descricao`; adiciona 3
    colunas de condição (nullable).
  - oferta_compra: adiciona volume_minimo_kg (float nullable) + 3 colunas de
    condição (nullable).

Idempotente — cada operação DDL é guardada por verificação prévia.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =============================================================================
# Helpers
# =============================================================================

def _insp():
    return sa.inspect(op.get_bind())


def _has_table(name: str) -> bool:
    return name in _insp().get_table_names()


def _has_column(table: str, col: str) -> bool:
    if not _has_table(table):
        return False
    return col in {c["name"] for c in _insp().get_columns(table)}


def _has_enum(name: str) -> bool:
    return bool(
        op.get_bind()
        .execute(sa.text("SELECT 1 FROM pg_type WHERE typname = :n"), {"n": name})
        .first()
    )


_LIMPEZA = ("limpo", "sujo", "contaminado")
_UMIDADE = ("seco", "umido", "molhado")
_FORMA = ("solto", "fardo", "prensado", "moido", "triturado", "granulado")


def _ensure_enum(name: str, values: tuple[str, ...]) -> None:
    if not _has_enum(name):
        labels = ", ".join(f"'{v}'" for v in values)
        op.execute(f"CREATE TYPE {name} AS ENUM ({labels})")


# =============================================================================
# upgrade / downgrade
# =============================================================================

def upgrade() -> None:
    # 1. Enums Postgres
    _ensure_enum("condicao_limpeza", _LIMPEZA)
    _ensure_enum("condicao_umidade", _UMIDADE)
    _ensure_enum("condicao_forma", _FORMA)

    # 2. anuncio_venda: drop titulo/descricao
    if _has_column("anuncio_venda", "titulo"):
        op.drop_column("anuncio_venda", "titulo")
    if _has_column("anuncio_venda", "descricao"):
        op.drop_column("anuncio_venda", "descricao")

    # 3. anuncio_venda: condição
    if not _has_column("anuncio_venda", "condicao_limpeza"):
        op.add_column(
            "anuncio_venda",
            sa.Column(
                "condicao_limpeza",
                sa.Enum(*_LIMPEZA, name="condicao_limpeza", create_type=False),
                nullable=True,
            ),
        )
    if not _has_column("anuncio_venda", "condicao_umidade"):
        op.add_column(
            "anuncio_venda",
            sa.Column(
                "condicao_umidade",
                sa.Enum(*_UMIDADE, name="condicao_umidade", create_type=False),
                nullable=True,
            ),
        )
    if not _has_column("anuncio_venda", "condicao_forma"):
        op.add_column(
            "anuncio_venda",
            sa.Column(
                "condicao_forma",
                sa.Enum(*_FORMA, name="condicao_forma", create_type=False),
                nullable=True,
            ),
        )

    # 4. oferta_compra: volume_minimo_kg + condição
    if not _has_column("oferta_compra", "volume_minimo_kg"):
        op.add_column(
            "oferta_compra",
            sa.Column("volume_minimo_kg", sa.Float, nullable=True),
        )
    if not _has_column("oferta_compra", "condicao_limpeza"):
        op.add_column(
            "oferta_compra",
            sa.Column(
                "condicao_limpeza",
                sa.Enum(*_LIMPEZA, name="condicao_limpeza", create_type=False),
                nullable=True,
            ),
        )
    if not _has_column("oferta_compra", "condicao_umidade"):
        op.add_column(
            "oferta_compra",
            sa.Column(
                "condicao_umidade",
                sa.Enum(*_UMIDADE, name="condicao_umidade", create_type=False),
                nullable=True,
            ),
        )
    if not _has_column("oferta_compra", "condicao_forma"):
        op.add_column(
            "oferta_compra",
            sa.Column(
                "condicao_forma",
                sa.Enum(*_FORMA, name="condicao_forma", create_type=False),
                nullable=True,
            ),
        )


def downgrade() -> None:
    # 1. oferta_compra: drop condição + volume_minimo_kg
    for col in ("condicao_forma", "condicao_umidade", "condicao_limpeza", "volume_minimo_kg"):
        if _has_column("oferta_compra", col):
            op.drop_column("oferta_compra", col)

    # 2. anuncio_venda: drop condição
    for col in ("condicao_forma", "condicao_umidade", "condicao_limpeza"):
        if _has_column("anuncio_venda", col):
            op.drop_column("anuncio_venda", col)

    # 3. anuncio_venda: restaura titulo/descricao
    if not _has_column("anuncio_venda", "titulo"):
        op.add_column(
            "anuncio_venda",
            sa.Column("titulo", sa.String(150), nullable=False, server_default=sa.text("''")),
        )
        # Remove default depois do backfill implícito (linhas existentes ficam '')
        op.alter_column("anuncio_venda", "titulo", server_default=None)
    if not _has_column("anuncio_venda", "descricao"):
        op.add_column(
            "anuncio_venda",
            sa.Column("descricao", sa.Text, nullable=True),
        )

    # 4. Drop enums (depois de qualquer uso por colunas).
    #    Verificação: só dropa se nenhuma coluna usa o tipo.
    for enum_name in ("condicao_forma", "condicao_umidade", "condicao_limpeza"):
        usage = op.get_bind().execute(
            sa.text(
                "SELECT 1 FROM pg_type t JOIN pg_attribute a ON a.atttypid = t.oid "
                "WHERE t.typname = :n LIMIT 1"
            ),
            {"n": enum_name},
        ).first()
        if not usage:
            op.execute(f"DROP TYPE IF EXISTS {enum_name}")
