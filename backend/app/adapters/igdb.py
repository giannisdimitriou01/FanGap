"""IGDB adapter. Twitch client-credentials OAuth, then Apicalypse query."""

from __future__ import annotations

import sys
import time

import httpx

from app.adapters.base import AdapterConfigError, AdapterError, GameRef, RawRating
from app.core.config import settings
from app.models.enums import RatingAudience, RatingSource

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
GAMES_URL = "https://api.igdb.com/v4/games"


class IGDBAdapter:
    source = RatingSource.IGDB

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.client_id = client_id if client_id is not None else settings.igdb_client_id
        self.client_secret = (
            client_secret if client_secret is not None else settings.igdb_client_secret
        )
        self._client = client or httpx.Client(timeout=20.0)
        self._owns_client = client is None
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _access_token(self) -> str:
        if not self.client_id or not self.client_secret:
            raise AdapterConfigError("IGDB_CLIENT_ID / IGDB_CLIENT_SECRET are not configured")
        if self.client_id == "your_twitch_client_id":
            raise AdapterConfigError("IGDB_CLIENT_ID / IGDB_CLIENT_SECRET are not configured")
        now = time.time()
        if self._token and now < self._token_expires_at - 60:
            return self._token

        try:
            response = self._client.post(
                TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AdapterError("IGDB OAuth token request failed") from exc

        self._token = payload["access_token"]
        self._token_expires_at = now + int(payload.get("expires_in", 0))
        return self._token

    def fetch_ratings(self, game: GameRef) -> list[RawRating]:
        if game.igdb_id is None:
            return []

        token = self._access_token()
        query = (
            "fields aggregated_rating,aggregated_rating_count,rating,rating_count; "
            f"where id = {int(game.igdb_id)};"
        )
        try:
            response = self._client.post(
                GAMES_URL,
                headers={
                    "Client-ID": self.client_id,
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
                content=query,
            )
            response.raise_for_status()
            rows = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AdapterError(f"IGDB request failed for game {game.igdb_id}") from exc

        if not rows:
            return []

        row = rows[0]
        ratings: list[RawRating] = []

        critic_score = row.get("aggregated_rating")
        if critic_score is not None:
            ratings.append(
                RawRating(
                    source=self.source,
                    audience=RatingAudience.CRITIC,
                    raw_score=float(critic_score),
                    scale_max=100.0,
                    review_count=row.get("aggregated_rating_count"),
                )
            )

        user_score = row.get("rating")
        if user_score is not None:
            ratings.append(
                RawRating(
                    source=self.source,
                    audience=RatingAudience.FAN,
                    raw_score=float(user_score),
                    scale_max=100.0,
                    review_count=row.get("rating_count"),
                )
            )

        return ratings


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    igdb_id = int(args[0]) if args else 113112
    adapter = IGDBAdapter()
    try:
        ratings = adapter.fetch_ratings(GameRef(title="standalone", igdb_id=igdb_id))
        print([rating.as_dict() for rating in ratings] or "no ratings")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
