"""Rotas — Dispositivos (token push FCM/APNs registrado pelo app)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.conteudo import DispositivoRead, DispositivoRegister
from app.services.conteudo_service import ConteudoService

router = APIRouter(prefix="/api/dispositivos", tags=["dispositivos"])


@router.post("/token", response_model=DispositivoRead, status_code=status.HTTP_201_CREATED)
async def registrar(
    payload: DispositivoRegister,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = ConteudoService(db)
    d = await svc.registrar_dispositivo(
        usuario_id=current_user.id,
        plataforma=payload.plataforma,
        token=payload.token,
        modelo=payload.modelo,
        versao_app=payload.versao_app,
    )
    await db.commit()
    return d
