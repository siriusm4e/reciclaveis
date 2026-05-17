"""Garante .gitkeep nas subpastas de storage (para volume vazio rodar)."""

from __future__ import annotations

import os

from app.core.config import settings

SUBDIRS = ("documentos", "anuncios", "avatares", "conteudo")


def ensure_storage_dirs() -> None:
    base = settings.STORAGE_BASE_PATH
    for sub in SUBDIRS:
        path = os.path.join(base, sub)
        os.makedirs(path, exist_ok=True)
