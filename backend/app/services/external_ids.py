"""Resolve OpenCritic ids best-effort for live ranking."""

from __future__ import annotations

import httpx

from app.adapters.base import AdapterConfigError
from app.core.config import settings

OPENCRITIC_SEARCH_URL = "https://opencritic-api.p.rapidapi.com/game/search"
OPENCRITIC_HOST = "opencritic-api.p.rapidapi.com"


def resolve_opencritic_id(title: str, client: httpx.Client | None = None) -> int | None:
    key = settings.opencritic_rapidapi_key
    if not key or key == "your_key_here":
        return None
    http = client or httpx.Client(timeout=15.0)
    owns = client is None
    try:
        response = http.get(
            OPENCRITIC_SEARCH_URL,
            params={"criteria": title},
            headers={
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": OPENCRITIC_HOST,
            },
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            return None
        first = rows[0]
        oc_id = first.get("id") or first.get("ID")
        return int(oc_id) if oc_id is not None else None
    except (httpx.HTTPError, ValueError, TypeError, KeyError):
        return None
    finally:
        if owns:
            http.close()


def game_ref_from_catalog_row(row: dict, *, resolve_opencritic: bool = True):
    from app.adapters.base import GameRef

    opencritic_id = None
    if resolve_opencritic:
        opencritic_id = resolve_opencritic_id(row["title"])
    return GameRef(
        title=row["title"],
        steam_app_id=row.get("steam_app_id"),
        opencritic_id=opencritic_id,
        igdb_id=row["igdb_id"],
    )
