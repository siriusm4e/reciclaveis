"""Upload — validação MIME real (python-magic), limite de tamanho, nome UUID."""

from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO, Literal
from uuid import uuid4

import magic

from app.core.config import settings
from app.core.exceptions import ValidationDomainError


Subpasta = Literal["documentos", "anuncios", "avatares", "conteudo"]


_MIME_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}


def _detect_mime(buf: bytes) -> str:
    """Detecta MIME real do conteúdo (não confia em Content-Type do cliente)."""
    return magic.from_buffer(buf, mime=True)


def validar_e_salvar(
    *,
    file_obj: BinaryIO,
    subpasta: Subpasta,
    declared_filename: str | None = None,
) -> tuple[str, str, int]:
    """Lê stream, valida MIME e tamanho, persiste com nome UUID.

    Retorna (relative_path, mime_real, tamanho_bytes).
    Levanta `ValidationDomainError` em qualquer falha.
    """
    file_obj.seek(0)
    chunks = []
    total = 0
    while True:
        chunk = file_obj.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > settings.UPLOAD_MAX_BYTES:
            raise ValidationDomainError(
                "Arquivo excede o tamanho máximo permitido",
                details={"max_bytes": settings.UPLOAD_MAX_BYTES},
            )
        chunks.append(chunk)
    payload = b"".join(chunks)

    if not payload:
        raise ValidationDomainError("Arquivo vazio")

    mime = _detect_mime(payload[: 64 * 1024])
    if mime not in settings.upload_allowed_mime_set:
        raise ValidationDomainError(
            "Tipo de arquivo não permitido",
            details={"mime": mime, "permitidos": sorted(settings.upload_allowed_mime_set)},
        )

    # Extensão derivada do MIME real — ignora extensão declarada do cliente
    ext = _MIME_EXT.get(mime) or Path(declared_filename or "").suffix or ""
    nome = f"{uuid4().hex}{ext}"

    base = Path(settings.STORAGE_BASE_PATH) / subpasta
    base.mkdir(parents=True, exist_ok=True)
    destino = base / nome
    destino.write_bytes(payload)

    rel = os.path.join(subpasta, nome).replace(os.sep, "/")
    return rel, mime, total


def url_publica(relative_path: str) -> str:
    base = settings.STORAGE_PUBLIC_URL.rstrip("/")
    return f"{base}/{relative_path.lstrip('/')}"
