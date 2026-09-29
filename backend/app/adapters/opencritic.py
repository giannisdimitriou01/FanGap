"""OpenCritic critic-score adapter. Auth is a RapidAPI key header."""

from __future__ import annotations

import sys

import httpx

from app.adapters.base import AdapterConfigError, AdapterError, GameRef, RawRating
from app.core.config import settings
from app.models.enums import RatingAudience, RatingSource

OPENCRITIC_HOST = "opencritic-api.p.rapidapi.com"
OPENCRITIC_GAME_URL = "https://opencritic-api.p.rapidapi.com/game/{game_id}"


class OpenCriticAdapter:
    source = RatingSource.OPENCRITIC

    def __init__(
        self,
        api_key: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.opencritic_rapidapi_key
        self._client = client or httpx.Client(timeout=20.0)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def fetch_ratings(self, game: GameRef) -> list[RawRating]:
        if not self.api_key or self.api_key == "your_key_here":
            raise AdapterConfigError("OPENCRITIC_RAPIDAPI_KEY is not configured")
        if game.opencritic_id is None:
            return []

        try:
            response = self._client.get(
                OPENCRITIC_GAME_URL.format(game_id=game.opencritic_id),
                headers={
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": OPENCRITIC_HOST,
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AdapterError(
                f"OpenCritic request failed for game {game.opencritic_id}"
            ) from exc

        score = payload.get("topCriticScore")
        if score is None or score < 0:
            return []

        review_count = payload.get("numReviews")
        return [
            RawRating(
                source=self.source,
                audience=RatingAudience.CRITIC,
                raw_score=float(score),
                scale_max=100.0,
                review_count=int(review_count) if review_count is not None else None,
            )
        ]


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    opencritic_id = int(args[0]) if args else 10181
    adapter = OpenCriticAdapter()
    try:
        ratings = adapter.fetch_ratings(
            GameRef(title="standalone", opencritic_id=opencritic_id)
        )
        print([rating.as_dict() for rating in ratings] or "no ratings")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
