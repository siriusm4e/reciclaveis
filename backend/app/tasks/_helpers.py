"""Helper para executar coro async dentro de tasks Celery sync."""

from __future__ import annotations

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")


def run_async(coro: Awaitable[T]) -> T:
    """Executa um Awaitable em loop dedicado. Use dentro de @celery_app.task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Em worker já com loop rodando — cria novo
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        return loop.run_until_complete(coro)
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
