"""Integração Receita Federal — CPF/CNPJ.

Interface única `consultar_cpf` / `consultar_cnpj`. Implementação no MVP é stub
que valida apenas o dígito verificador. Em produção, plugar provedor real.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.core.exceptions import ValidationDomainError


@dataclass(frozen=True)
class CPFData:
    cpf: str
    nome: str | None
    situacao: str  # ativo | suspensa | titular_falecido | baixado | nula


@dataclass(frozen=True)
class CNPJData:
    cnpj: str
    razao_social: str | None
    nome_fantasia: str | None
    situacao: str  # ativa | suspensa | inapta | baixada | nula
    porte: str | None  # MEI | EPP | ME | DEMAIS
    cnae_principal: str | None
    socios: list[dict] | None


# === Validação algorítmica (independe do provedor) ===

def _valida_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or not cpf.isdigit() or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        s = sum(int(cpf[n]) * ((i + 1) - n) for n in range(i))
        d = (s * 10) % 11
        d = 0 if d == 10 else d
        if d != int(cpf[i]):
            return False
    return True


def _valida_cnpj(cnpj: str) -> bool:
    if len(cnpj) != 14 or not cnpj.isdigit() or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    for digito, pesos in ((12, pesos1), (13, pesos2)):
        s = sum(int(cnpj[i]) * pesos[i] for i in range(digito))
        d = 11 - (s % 11)
        d = 0 if d >= 10 else d
        if d != int(cnpj[digito]):
            return False
    return True


# === Provedores ===

class _ReceitaProvider:
    async def consultar_cpf(self, cpf: str) -> CPFData: ...
    async def consultar_cnpj(self, cnpj: str) -> CNPJData: ...


class _StubProvider(_ReceitaProvider):
    """Valida apenas dígitos; assume situação ativa. Para uso em DEV/CI."""

    async def consultar_cpf(self, cpf: str) -> CPFData:
        if not _valida_cpf(cpf):
            raise ValidationDomainError("CPF inválido", details={"cpf": cpf})
        return CPFData(cpf=cpf, nome=None, situacao="ativo")

    async def consultar_cnpj(self, cnpj: str) -> CNPJData:
        if not _valida_cnpj(cnpj):
            raise ValidationDomainError("CNPJ inválido", details={"cnpj": cnpj})
        return CNPJData(
            cnpj=cnpj,
            razao_social=None,
            nome_fantasia=None,
            situacao="ativa",
            porte=None,
            cnae_principal=None,
            socios=None,
        )


def get_provider() -> _ReceitaProvider:
    # Plugar HubDev / Serpro aqui quando RECEITA_PROVIDER != "stub"
    return _StubProvider()


__all__ = ["CPFData", "CNPJData", "get_provider"]
