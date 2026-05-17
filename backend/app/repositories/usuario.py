"""Repositório de Usuario."""

from __future__ import annotations

from sqlalchemy import select

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    model = Usuario

    async def get_by_email(self, email: str) -> Usuario | None:
        return await self.db.scalar(select(Usuario).where(Usuario.email == email))

    async def get_by_cpf(self, cpf: str) -> Usuario | None:
        return await self.db.scalar(select(Usuario).where(Usuario.cpf == cpf))

    async def get_by_telefone(self, telefone: str) -> Usuario | None:
        return await self.db.scalar(select(Usuario).where(Usuario.telefone == telefone))
