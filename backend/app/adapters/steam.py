"""Steam user-review adapter. No API key — percent-positive is already 0–100."""

from __future__ import annotations

import sys

import httpx

from app.adapters.base import AdapterError, GameRef, RawRating
from app.models.enums import RatingAudience, RatingSource

STEAM_REVIEW_URL = "https://store.steampowered.com/appreviews/{app_id}"
DEFAULT_HEADERS = {"User-Agent": "FanGap/0.1 (portfolio ratings tracker)"}


class SteamAdapter:
    source = RatingSource.STEAM

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=20.0, headers=DEFAULT_HEADERS)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def fetch_ratings(self, game: GameRef) -> list[RawRating]:
        if game.steam_app_id is None:
            return []

        url = STEAM_REVIEW_URL.format(app_id=game.steam_app_id)
        try:
            response = self._client.get(
                url,
                params={
                    "json": 1,
                    "language": "all",
                    "purchase_type": "all",
                    "num_per_page": 0,
                    "filter": "all",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AdapterError(f"Steam request failed for app {game.steam_app_id}") from exc

        if payload.get("success") != 1:
            return []

        summary = payload.get("query_summary") or {}
        total_reviews = summary.get("total_reviews") or 0
        total_positive = summary.get("total_positive") or 0
        if total_reviews <= 0:
            return []

        percent_positive = (total_positive / total_reviews) * 100
        return [
            RawRating(
                source=self.source,
                audience=RatingAudience.FAN,
                raw_score=percent_positive,
                scale_max=100.0,
                review_count=int(total_reviews),
            )
        ]


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    app_id = int(args[0]) if args else 1145360
    adapter = SteamAdapter()
    try:
        ratings = adapter.fetch_ratings(
            GameRef(title="standalone", steam_app_id=app_id)
        )
        print([rating.as_dict() for rating in ratings] or "no ratings")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
