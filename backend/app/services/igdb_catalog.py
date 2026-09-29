"""IGDB Apicalypse queries for search, metadata, and leaderboard pools."""

from __future__ import annotations

from datetime import date, datetime, timezone

import httpx

from app.adapters.base import AdapterConfigError, AdapterError
from app.adapters.igdb import IGDBAdapter, GAMES_URL
from app.core.config import settings


STEAM_EXTERNAL_CATEGORY = 1


def _epoch_to_date(value: int | None) -> date | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).date()


def _cover_url(cover: dict | None) -> str | None:
    if not cover:
        return None
    url = cover.get("url")
    if not url:
        return None
    if url.startswith("//"):
        return f"https:{url}".replace("t_thumb", "t_cover_big")
    return url.replace("t_thumb", "t_cover_big")


def _steam_app_id(row: dict) -> int | None:
    for external in row.get("external_games") or []:
        if external.get("category") == STEAM_EXTERNAL_CATEGORY:
            uid = external.get("uid")
            if uid is not None:
                try:
                    return int(uid)
                except (TypeError, ValueError):
                    continue
    return None


def _map_row(row: dict) -> dict:
    genres = sorted({g.get("name") for g in (row.get("genres") or []) if g.get("name")})
    platforms = sorted({p.get("name") for p in (row.get("platforms") or []) if p.get("name")})
    return {
        "igdb_id": int(row["id"]),
        "title": row.get("name") or "Unknown",
        "release_date": _epoch_to_date(row.get("first_release_date")),
        "genres": genres,
        "platforms": platforms,
        "cover_url": _cover_url(row.get("cover")),
        "steam_app_id": _steam_app_id(row),
    }


class IGDBCatalogClient:
    def __init__(self, adapter: IGDBAdapter | None = None) -> None:
        self._adapter = adapter or IGDBAdapter()
        self._owns_adapter = adapter is None

    def close(self) -> None:
        if self._owns_adapter:
            self._adapter.close()

    def _post(self, query: str) -> list[dict]:
        token = self._adapter._access_token()
        client_id = self._adapter.client_id
        try:
            response = self._adapter._client.post(
                GAMES_URL,
                headers={
                    "Client-ID": client_id,
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
                content=query,
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AdapterError("IGDB catalog request failed") from exc

    def search_games(self, q: str, *, limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
        if not settings.igdb_client_id or not settings.igdb_client_secret:
            raise AdapterConfigError("IGDB credentials are not configured")
        safe = q.replace('"', "").strip()
        if not safe:
            query = (
                "fields id,name,cover.url,first_release_date,genres.name,platforms.name,external_games.*; "
                f"where version_parent = null; sort total_rating_count desc; limit {limit}; offset {offset};"
            )
        else:
            query = (
                "fields id,name,cover.url,first_release_date,genres.name,platforms.name,external_games.*; "
                f'search "{safe}"; '
                "where version_parent = null; "
                f"limit {limit}; offset {offset};"
            )
        rows = self._post(query)
        items = [_map_row(row) for row in rows]
        total = offset + len(items) + (1 if len(items) == limit else 0)
        return items, total

    def get_game(self, igdb_id: int) -> dict | None:
        query = (
            "fields id,name,cover.url,first_release_date,genres.name,platforms.name,external_games.*; "
            f"where id = {int(igdb_id)};"
        )
        rows = self._post(query)
        if not rows:
            return None
        return _map_row(rows[0])

    def candidate_pool(self, limit: int = 150) -> list[dict]:
        query = (
            "fields id,name,cover.url,first_release_date,genres.name,platforms.name,external_games.*; "
            "where aggregated_rating > 0 & rating > 0 & version_parent = null; "
            "sort total_rating_count desc; "
            f"limit {limit};"
        )
        rows = self._post(query)
        return [_map_row(row) for row in rows]
