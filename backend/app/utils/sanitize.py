"""Sanitização de texto livre — XSS via bleach."""

from __future__ import annotations

import bleach

# Mensagens de chat: apenas formatação básica
ALLOWED_TAGS_CHAT: list[str] = []
ALLOWED_ATTRIBUTES_CHAT: dict[str, list[str]] = {}

# Conteúdo educativo / descrições: HTML enriquecido moderado
ALLOWED_TAGS_RICH = [
    "p", "br", "strong", "em", "ul", "ol", "li", "a", "h2", "h3", "h4",
    "blockquote", "code", "pre",
]
ALLOWED_ATTRIBUTES_RICH = {"a": ["href", "title", "rel"]}


def sanitize_chat(text: str) -> str:
    """Strip total de HTML — chat é texto puro."""
    return bleach.clean(text, tags=ALLOWED_TAGS_CHAT, attributes=ALLOWED_ATTRIBUTES_CHAT, strip=True)


def sanitize_rich(html: str) -> str:
    """Sanitiza HTML enriquecido (descrições, conteúdo educativo)."""
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS_RICH,
        attributes=ALLOWED_ATTRIBUTES_RICH,
        strip=True,
    )
    return bleach.linkify(cleaned, callbacks=[bleach.callbacks.nofollow])
