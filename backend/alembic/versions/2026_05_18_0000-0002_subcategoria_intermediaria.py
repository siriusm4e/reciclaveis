"""Introduz nível intermediário Subcategoria e renomeia antiga subcategoria → tipo_material.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-18 00:00:00

Contexto:
    A migration 0001 usa ``Base.metadata.create_all()`` — em fresh installs cria
    a estrutura **nova** diretamente. Em DBs que rodaram 0001 com o schema
    antigo, ``subcategoria`` tem ``unidade_padrao`` e não existe ``tipo_material``.

    Esta migration é **idempotente**: cada operação DDL é guardada por
    verificação prévia para sobreviver a:
      - Fresh install (sub+tipo já no formato novo → no-op).
      - Legacy completo (rename + create + repoint).
      - Estado parcial (re-run após falha anterior).

    Convenção de naming (PostgreSQL não renomeia constraints/índices junto com
    a tabela): ``pk_<tabela>``, ``fk_<tabela>_<coluna>_<referida>``,
    ``uq_<tabela>_<coluna>``, ``ix_<tabela>_<coluna>``. Renomeamos
    explicitamente após ``RENAME TABLE``.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =============================================================================
# Helpers idempotentes — todas as operações DDL passam por aqui.
# =============================================================================

def _insp(bind=None):
    return sa.inspect(bind or op.get_bind())


def _has_table(name: str) -> bool:
    return name in _insp().get_table_names()


def _has_column(table: str, col: str) -> bool:
    if not _has_table(table):
        return False
    return col in {c["name"] for c in _insp().get_columns(table)}


def _has_index(table: str, name: str) -> bool:
    if not _has_table(table):
        return False
    return name in {i["name"] for i in _insp().get_indexes(table)}


def _has_constraint(table: str, name: str) -> bool:
    if not _has_table(table):
        return False
    insp = _insp()
    if (insp.get_pk_constraint(table) or {}).get("name") == name:
        return True
    if name in {fk["name"] for fk in insp.get_foreign_keys(table)}:
        return True
    if name in {uq["name"] for uq in insp.get_unique_constraints(table)}:
        return True
    return False


def _safe_rename_column(table: str, old: str, new: str) -> None:
    if _has_column(table, old) and not _has_column(table, new):
        op.alter_column(table, old, new_column_name=new)


def _safe_drop_constraint(table: str, name: str) -> None:
    op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}")


def _safe_rename_constraint(table: str, old: str, new: str) -> None:
    if _has_constraint(table, old) and not _has_constraint(table, new):
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old} TO {new}")


def _safe_rename_index(old: str, new: str) -> None:
    op.execute(f"ALTER INDEX IF EXISTS {old} RENAME TO {new}")


def _safe_drop_index(table: str, name: str) -> None:
    if _has_index(table, name):
        op.drop_index(name, table_name=table)


def _safe_drop_column(table: str, col: str) -> None:
    if _has_column(table, col):
        op.drop_column(table, col)


# =============================================================================
# upgrade / downgrade
# =============================================================================

def upgrade() -> None:
    sub_has_unidade = _has_column("subcategoria", "unidade_padrao")
    tipo_exists = _has_table("tipo_material")

    # Fresh install detection: subcategoria já está no formato novo
    # (sem unidade_padrao) e tipo_material já existe → nada a fazer.
    if not sub_has_unidade and tipo_exists:
        return

    # ------------------------------------------------------------------
    # 1. Renomeia FK columns em anuncio_venda / oferta_compra
    # ------------------------------------------------------------------
    _safe_rename_column("anuncio_venda", "subcategoria_id", "tipo_material_id")
    _safe_rename_column("oferta_compra", "subcategoria_id", "tipo_material_id")

    # ------------------------------------------------------------------
    # 2. Renomeia tabela subcategoria → tipo_material (se aplicável)
    #    + renomeia PK constraint + índices carregados pela tabela velha.
    # ------------------------------------------------------------------
    if sub_has_unidade and not tipo_exists:
        # Drop UQ antiga (categoria_id, slug) — será recriada depois com nova coluna
        _safe_drop_constraint("subcategoria", "uq_subcategoria_categoria_slug")

        op.rename_table("subcategoria", "tipo_material")

        # PK e índices não migram nomes automaticamente no Postgres
        _safe_rename_constraint("tipo_material", "pk_subcategoria", "pk_tipo_material")
        _safe_rename_index("ix_subcategoria_categoria_id", "ix_tipo_material_categoria_id_legacy")
        _safe_rename_index("ix_subcategoria_ativo", "ix_tipo_material_ativo")
        _safe_rename_index("ix_subcategoria_categoria_id_slug", "ix_tipo_material_categoria_id_slug")

        # FK em anuncio_venda/oferta_compra (FK constraint name não migra)
        # — renomeia para alinhar à convenção, ignora se não existir.
        _safe_rename_constraint(
            "anuncio_venda",
            "fk_anuncio_venda_subcategoria_id_subcategoria",
            "fk_anuncio_venda_tipo_material_id_tipo_material",
        )
        _safe_rename_constraint(
            "oferta_compra",
            "fk_oferta_compra_subcategoria_id_subcategoria",
            "fk_oferta_compra_tipo_material_id_tipo_material",
        )

    # ------------------------------------------------------------------
    # 3. Cria nova tabela subcategoria (intermediária) se ausente
    # ------------------------------------------------------------------
    if not _has_table("subcategoria"):
        op.create_table(
            "subcategoria",
            sa.Column(
                "id",
                PG_UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "categoria_id",
                PG_UUID(as_uuid=True),
                sa.ForeignKey("categoria.id", ondelete="CASCADE", name="fk_subcategoria_categoria_id_categoria"),
                nullable=False,
            ),
            sa.Column("nome", sa.String(120), nullable=False),
            sa.Column("slug", sa.String(120), nullable=False),
            sa.Column(
                "requer_validacao_documental",
                sa.Boolean,
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "documentos_exigidos",
                JSONB,
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column("ordem", sa.Integer, nullable=False, server_default=sa.text("100")),
            sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.PrimaryKeyConstraint("id", name="pk_subcategoria"),
            sa.UniqueConstraint("categoria_id", "slug", name="uq_subcategoria_categoria_slug"),
        )

    if not _has_index("subcategoria", "ix_subcategoria_categoria_id"):
        op.create_index("ix_subcategoria_categoria_id", "subcategoria", ["categoria_id"])
    if not _has_index("subcategoria", "ix_subcategoria_ativo"):
        op.create_index("ix_subcategoria_ativo", "subcategoria", ["ativo"])

    # ------------------------------------------------------------------
    # 4. Data migration legado: cria "Geral" por categoria que tenha tipo_material
    #    Idempotente via WHERE NOT EXISTS.
    # ------------------------------------------------------------------
    if _has_table("tipo_material") and _has_column("tipo_material", "categoria_id"):
        op.execute(
            """
            INSERT INTO subcategoria (id, categoria_id, nome, slug, requer_validacao_documental,
                                      documentos_exigidos, ordem, ativo)
            SELECT gen_random_uuid(), c.id, 'Geral', 'geral',
                   COALESCE(bool_or(tm.requer_validacao_documental), false),
                   COALESCE(
                       (SELECT jsonb_agg(DISTINCT elem)
                        FROM tipo_material tm2,
                             jsonb_array_elements_text(tm2.documentos_exigidos) AS elem
                        WHERE tm2.categoria_id = c.id),
                       '[]'::jsonb
                   ),
                   100, true
            FROM categoria c
            JOIN tipo_material tm ON tm.categoria_id = c.id
            WHERE NOT EXISTS (
                SELECT 1 FROM subcategoria s
                WHERE s.categoria_id = c.id AND s.slug = 'geral'
            )
            GROUP BY c.id
            """
        )

    # ------------------------------------------------------------------
    # 5. Adiciona tipo_material.subcategoria_id + backfill + FK + index + UQ
    # ------------------------------------------------------------------
    if _has_table("tipo_material") and not _has_column("tipo_material", "subcategoria_id"):
        op.add_column(
            "tipo_material",
            sa.Column("subcategoria_id", PG_UUID(as_uuid=True), nullable=True),
        )

    if _has_column("tipo_material", "subcategoria_id") and _has_column("tipo_material", "categoria_id"):
        op.execute(
            """
            UPDATE tipo_material tm
            SET subcategoria_id = s.id
            FROM subcategoria s
            WHERE s.categoria_id = tm.categoria_id
              AND s.slug = 'geral'
              AND tm.subcategoria_id IS NULL
            """
        )

    if _has_column("tipo_material", "subcategoria_id"):
        # NOT NULL só após backfill garantido
        col = next(
            (c for c in _insp().get_columns("tipo_material") if c["name"] == "subcategoria_id"),
            None,
        )
        if col and col.get("nullable", True):
            # Confirma backfill completo antes de aplicar NOT NULL
            null_count = op.get_bind().execute(
                sa.text("SELECT count(*) FROM tipo_material WHERE subcategoria_id IS NULL")
            ).scalar() or 0
            if null_count == 0:
                op.alter_column("tipo_material", "subcategoria_id", nullable=False)

    if not _has_constraint("tipo_material", "fk_tipo_material_subcategoria_id_subcategoria"):
        op.create_foreign_key(
            "fk_tipo_material_subcategoria_id_subcategoria",
            "tipo_material",
            "subcategoria",
            ["subcategoria_id"],
            ["id"],
            ondelete="CASCADE",
        )
    if not _has_index("tipo_material", "ix_tipo_material_subcategoria_id"):
        op.create_index(
            "ix_tipo_material_subcategoria_id", "tipo_material", ["subcategoria_id"]
        )
    if not _has_constraint("tipo_material", "uq_tipo_material_subcategoria_slug"):
        op.create_unique_constraint(
            "uq_tipo_material_subcategoria_slug",
            "tipo_material",
            ["subcategoria_id", "slug"],
        )

    # ------------------------------------------------------------------
    # 6. Re-aponta oportunidade.subcategoria_id (granular antigo → intermediário)
    # ------------------------------------------------------------------
    if _has_table("oportunidade") and _has_table("tipo_material"):
        # Só atualiza linhas cujo id ainda existe em tipo_material (granular antigo)
        op.execute(
            """
            UPDATE oportunidade o
            SET subcategoria_id = tm.subcategoria_id
            FROM tipo_material tm
            WHERE o.subcategoria_id = tm.id
              AND tm.subcategoria_id IS NOT NULL
            """
        )
        # FK constraint: dropa nomes possíveis e recria apontando para subcategoria
        for fk_name in (
            "fk_oportunidade_subcategoria_id_subcategoria",
            "oportunidade_subcategoria_id_fkey",
        ):
            _safe_drop_constraint("oportunidade", fk_name)
        if not _has_constraint(
            "oportunidade", "fk_oportunidade_subcategoria_id_subcategoria"
        ):
            op.create_foreign_key(
                "fk_oportunidade_subcategoria_id_subcategoria",
                "oportunidade",
                "subcategoria",
                ["subcategoria_id"],
                ["id"],
            )

    # ------------------------------------------------------------------
    # 7. Re-aponta assinatura_alerta.subcategoria_ids (JSONB list de UUIDs)
    # ------------------------------------------------------------------
    if _has_table("assinatura_alerta") and _has_table("tipo_material"):
        op.execute(
            """
            UPDATE assinatura_alerta aa
            SET subcategoria_ids = COALESCE((
                SELECT jsonb_agg(DISTINCT (tm.subcategoria_id)::text)
                FROM jsonb_array_elements_text(aa.subcategoria_ids) AS sid
                JOIN tipo_material tm ON tm.id::text = sid
                WHERE tm.subcategoria_id IS NOT NULL
            ), '[]'::jsonb)
            WHERE jsonb_typeof(aa.subcategoria_ids) = 'array'
              AND jsonb_array_length(aa.subcategoria_ids) > 0
            """
        )

    # ------------------------------------------------------------------
    # 8. Drop colunas legadas de tipo_material (defensivo)
    # ------------------------------------------------------------------
    # FK velha categoria_id (nomes possíveis)
    for fk_name in (
        "fk_subcategoria_categoria_id_categoria",
        "subcategoria_categoria_id_fkey",
    ):
        _safe_drop_constraint("tipo_material", fk_name)

    _safe_drop_index("tipo_material", "ix_tipo_material_categoria_id_legacy")
    _safe_drop_column("tipo_material", "categoria_id")
    _safe_drop_column("tipo_material", "requer_validacao_documental")
    _safe_drop_column("tipo_material", "documentos_exigidos")


def downgrade() -> None:
    if not _has_table("tipo_material"):
        return

    # 1. Recria colunas legadas em tipo_material
    if not _has_column("tipo_material", "categoria_id"):
        op.add_column(
            "tipo_material",
            sa.Column("categoria_id", PG_UUID(as_uuid=True), nullable=True),
        )
    if not _has_column("tipo_material", "requer_validacao_documental"):
        op.add_column(
            "tipo_material",
            sa.Column(
                "requer_validacao_documental",
                sa.Boolean,
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
    if not _has_column("tipo_material", "documentos_exigidos"):
        op.add_column(
            "tipo_material",
            sa.Column(
                "documentos_exigidos",
                JSONB,
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
        )

    # Backfill a partir da subcategoria intermediária
    if _has_table("subcategoria"):
        op.execute(
            """
            UPDATE tipo_material tm
            SET categoria_id = s.categoria_id,
                requer_validacao_documental = s.requer_validacao_documental,
                documentos_exigidos = s.documentos_exigidos
            FROM subcategoria s
            WHERE s.id = tm.subcategoria_id
            """
        )

    # Reverte oportunidade.subcategoria_id (intermediário → primeiro tipo)
    if _has_table("oportunidade"):
        _safe_drop_constraint("oportunidade", "fk_oportunidade_subcategoria_id_subcategoria")
        op.execute(
            """
            UPDATE oportunidade o
            SET subcategoria_id = (
                SELECT tm.id FROM tipo_material tm
                WHERE tm.subcategoria_id = o.subcategoria_id
                ORDER BY tm.ordem LIMIT 1
            )
            WHERE EXISTS (
                SELECT 1 FROM tipo_material tm WHERE tm.subcategoria_id = o.subcategoria_id
            )
            """
        )

    # Drop novidades em tipo_material
    _safe_drop_constraint("tipo_material", "fk_tipo_material_subcategoria_id_subcategoria")
    _safe_drop_constraint("tipo_material", "uq_tipo_material_subcategoria_slug")
    _safe_drop_index("tipo_material", "ix_tipo_material_subcategoria_id")
    _safe_drop_column("tipo_material", "subcategoria_id")

    # Drop subcategoria intermediária
    if _has_table("subcategoria"):
        _safe_drop_index("subcategoria", "ix_subcategoria_categoria_id")
        _safe_drop_index("subcategoria", "ix_subcategoria_ativo")
        op.drop_table("subcategoria")

    # Recria FK categoria_id em tipo_material + NOT NULL
    if _has_column("tipo_material", "categoria_id"):
        op.alter_column("tipo_material", "categoria_id", nullable=False)
        if not _has_constraint("tipo_material", "fk_tipo_material_categoria_id_categoria"):
            op.create_foreign_key(
                "fk_tipo_material_categoria_id_categoria",
                "tipo_material",
                "categoria",
                ["categoria_id"],
                ["id"],
                ondelete="CASCADE",
            )

    # Renomeia tipo_material → subcategoria + constraints/índices
    op.rename_table("tipo_material", "subcategoria")
    _safe_rename_constraint("subcategoria", "pk_tipo_material", "pk_subcategoria")
    _safe_rename_index("ix_tipo_material_ativo", "ix_subcategoria_ativo")
    _safe_rename_index("ix_tipo_material_categoria_id_legacy", "ix_subcategoria_categoria_id")
    if not _has_constraint("subcategoria", "uq_subcategoria_categoria_slug"):
        op.create_unique_constraint(
            "uq_subcategoria_categoria_slug", "subcategoria", ["categoria_id", "slug"]
        )

    # Re-aponta FKs em marketplace
    _safe_rename_column("anuncio_venda", "tipo_material_id", "subcategoria_id")
    _safe_rename_column("oferta_compra", "tipo_material_id", "subcategoria_id")
    _safe_rename_constraint(
        "anuncio_venda",
        "fk_anuncio_venda_tipo_material_id_tipo_material",
        "fk_anuncio_venda_subcategoria_id_subcategoria",
    )
    _safe_rename_constraint(
        "oferta_compra",
        "fk_oferta_compra_tipo_material_id_tipo_material",
        "fk_oferta_compra_subcategoria_id_subcategoria",
    )

    # Re-cria FK oportunidade.subcategoria_id apontando para subcategoria (granular)
    if _has_table("oportunidade") and not _has_constraint(
        "oportunidade", "fk_oportunidade_subcategoria_id_subcategoria"
    ):
        op.create_foreign_key(
            "fk_oportunidade_subcategoria_id_subcategoria",
            "oportunidade",
            "subcategoria",
            ["subcategoria_id"],
            ["id"],
        )
