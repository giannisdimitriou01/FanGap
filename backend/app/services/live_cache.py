"""In-process TTL cache for live IGDB scores."""

from __future__ import annotations

import time
from typing import Any, TypeVar

from app.core.config import settings

T = TypeVar("T")

_store: dict[str, tuple[float, Any]] = {}


def cache_get(key: str) -> Any | None:
    entry = _store.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if time.time() >= expires_at:
        _store.pop(key, None)
        return None
    return value


def cache_set(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    ttl = ttl_seconds if ttl_seconds is not None else settings.live_cache_ttl_seconds
    _store[key] = (time.time() + ttl, value)


def cache_clear() -> None:
    _store.clear()
