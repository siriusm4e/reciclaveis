"""Conteúdo educativo + Preferências + Dispositivos."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conteudo_educativo import ConteudoEducativo
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.repositories.conteudo import (
    ConteudoEducativoRepository,
    DispositivoRepository,
    PreferenciaRepository,
)
from app.utils.sanitize import sanitize_rich


class ConteudoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.conteudos = ConteudoEducativoRepository(db)
        self.preferencias = PreferenciaRepository(db)
        self.dispositivos = DispositivoRepository(db)

    async def listar_para_conta(
        self, *, papel_slug: str | None, categoria_slug: str | None
    ) -> list[ConteudoEducativo]:
        return await self.conteudos.listar_publicados(
            papel_slug=papel_slug, categoria_slug=categoria_slug
        )

    async def criar(self, *, conteudo: str | None = None, **kw) -> ConteudoEducativo:
        if conteudo:
            kw["conteudo"] = sanitize_rich(conteudo)
        obj = ConteudoEducativo(**kw)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def atualizar(self, obj: ConteudoEducativo, **kw) -> ConteudoEducativo:
        if "conteudo" in kw and kw["conteudo"] is not None:
            kw["conteudo"] = sanitize_rich(kw["conteudo"])
        for k, v in kw.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        return obj

    async def get_preferencias(self, conta_id: UUID) -> PreferenciaComunicacao:
        pref = await self.preferencias.get_da_conta(conta_id)
        if pref is None:
            pref = await self.preferencias.upsert(conta_id)
        return pref

    async def atualizar_preferencias(self, conta_id: UUID, **prefs) -> PreferenciaComunicacao:
        return await self.preferencias.upsert(conta_id, **prefs)

    async def registrar_dispositivo(
        self,
        *,
        usuario_id: UUID,
        plataforma: str,
        token: str,
        modelo: str | None,
        versao_app: str | None,
    ):
        return await self.dispositivos.upsert_token(
            usuario_id=usuario_id,
            plataforma=plataforma,
            token=token,
            modelo=modelo,
            versao_app=versao_app,
        )


__all__ = ["ConteudoService"]
