"""Créditos — projeção de saldo, compra de pacote, ajuste admin (ledger imutável)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationDomainError
from app.models.enums import TransacaoTipo
from app.models.transacao_credito import TransacaoCredito
from app.repositories.creditos import (
    PacoteCreditoRepository,
    TransacaoCreditoRepository,
)


class CreditosService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.transacoes = TransacaoCreditoRepository(db)
        self.pacotes = PacoteCreditoRepository(db)

    async def saldo(self, conta_id: UUID) -> int:
        return await self.transacoes.saldo(conta_id)

    async def comprar_pacote(
        self,
        *,
        conta_id: UUID,
        pacote_id: UUID,
        referencia_id: UUID | None = None,
    ) -> TransacaoCredito:
        pacote = await self.pacotes.get(pacote_id)
        if pacote is None or not pacote.ativo:
            raise NotFoundError("Pacote indisponível")
        total = pacote.creditos + pacote.bonus
        # Em produção: integração com gateway aqui e só credita após `aprovado`.
        # Para MVP, credita imediato e registra referência ao pagamento posterior.
        t = TransacaoCredito(
            conta_id=conta_id,
            tipo=TransacaoTipo.COMPRA,
            valor=total,
            descricao=f"Compra de pacote {pacote.nome} ({pacote.creditos}+{pacote.bonus})",
            referencia_tipo="pacote_credito",
            referencia_id=referencia_id or pacote_id,
        )
        self.db.add(t)
        await self.db.flush()
        return t

    async def debitar(
        self,
        *,
        conta_id: UUID,
        valor: int,
        descricao: str,
        referencia_tipo: str | None = None,
        referencia_id: UUID | None = None,
    ) -> TransacaoCredito:
        if valor <= 0:
            raise ValidationDomainError("Débito requer valor positivo")
        t = TransacaoCredito(
            conta_id=conta_id,
            tipo=TransacaoTipo.CONSUMO,
            valor=-valor,
            descricao=descricao,
            referencia_tipo=referencia_tipo,
            referencia_id=referencia_id,
        )
        self.db.add(t)
        await self.db.flush()
        return t

    async def reembolsar(
        self,
        *,
        conta_id: UUID,
        valor: int,
        descricao: str,
        referencia_tipo: str | None = None,
        referencia_id: UUID | None = None,
    ) -> TransacaoCredito:
        if valor <= 0:
            raise ValidationDomainError("Reembolso requer valor positivo")
        t = TransacaoCredito(
            conta_id=conta_id,
            tipo=TransacaoTipo.REEMBOLSO,
            valor=valor,
            descricao=descricao,
            referencia_tipo=referencia_tipo,
            referencia_id=referencia_id,
        )
        self.db.add(t)
        await self.db.flush()
        return t

    async def ajuste_admin(
        self,
        *,
        conta_id: UUID,
        valor: int,
        descricao: str,
        admin_id: UUID,
    ) -> TransacaoCredito:
        if valor == 0:
            raise ValidationDomainError("Ajuste com valor zero não é permitido")
        t = TransacaoCredito(
            conta_id=conta_id,
            tipo=TransacaoTipo.AJUSTE_ADMIN,
            valor=valor,
            descricao=descricao,
            admin_id=admin_id,
        )
        self.db.add(t)
        await self.db.flush()
        return t


__all__ = ["CreditosService"]
