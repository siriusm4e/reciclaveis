"""Disparo de comunicação segmentada com verificação de opt-in (LGPD by design)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationDomainError
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.repositories.conteudo import DispositivoRepository
from app.utils.notifications import enviar_push


# Mapeia finalidade → coluna de opt-in em PreferenciaComunicacao
FINALIDADE_TO_OPTIN = {
    "novidades_plataforma": "aceita_novidades_plataforma",
    "conteudo_educativo": "aceita_conteudo_educativo",
    "comunicacao_prefeitura_municipio": "aceita_comunicacao_prefeitura_municipio",
    "comunicacao_orgao_estadual": "aceita_comunicacao_orgao_estadual",
}


class NotificacaoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.dispositivos = DispositivoRepository(db)

    async def disparar_segmentado(
        self,
        *,
        finalidade: str,
        titulo: str,
        corpo: str,
        segmentacao: dict,
    ) -> dict:
        coluna = FINALIDADE_TO_OPTIN.get(finalidade)
        if coluna is None:
            raise ValidationDomainError("Finalidade não suportada")

        # Contas opt-in
        stmt = select(PreferenciaComunicacao.conta_id).where(
            getattr(PreferenciaComunicacao, coluna).is_(True)
        )
        contas = list(await self.db.scalars(stmt))

        tokens: list[str] = []
        for conta_id in contas:
            tokens.extend(await self.dispositivos.tokens_ativos_de_conta(conta_id))

        return enviar_push(
            tokens=tokens,
            titulo=titulo,
            corpo=corpo,
            data={"finalidade": finalidade, **{k: str(v) for k, v in (segmentacao or {}).items()}},
        )


__all__ = ["NotificacaoService", "FINALIDADE_TO_OPTIN"]
