import httpx

import pytest

from app.adapters.base import AdapterConfigError, GameRef
from app.adapters.igdb import IGDBAdapter
from app.adapters.opencritic import OpenCriticAdapter
from app.adapters.steam import SteamAdapter
from app.models.enums import RatingAudience, RatingSource


def test_steam_percent_positive() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "1145360" in str(request.url)
        return httpx.Response(
            200,
            json={
                "success": 1,
                "query_summary": {
                    "total_positive": 97,
                    "total_negative": 3,
                    "total_reviews": 100,
                },
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = SteamAdapter(client=client)
    ratings = adapter.fetch_ratings(GameRef(title="Hades", steam_app_id=1145360))
    assert len(ratings) == 1
    assert ratings[0].source == RatingSource.STEAM
    assert ratings[0].audience == RatingAudience.FAN
    assert ratings[0].raw_score == 97.0
    assert ratings[0].review_count == 100


def test_steam_skips_missing_app_id() -> None:
    adapter = SteamAdapter(client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
    assert adapter.fetch_ratings(GameRef(title="Unknown")) == []


def test_opencritic_top_critic_score() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-RapidAPI-Key"] == "test-key"
        return httpx.Response(
            200,
            json={"topCriticScore": 94, "numReviews": 191},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = OpenCriticAdapter(api_key="test-key", client=client)
    ratings = adapter.fetch_ratings(GameRef(title="Hades", opencritic_id=10181))
    assert len(ratings) == 1
    assert ratings[0].source == RatingSource.OPENCRITIC
    assert ratings[0].audience == RatingAudience.CRITIC
    assert ratings[0].raw_score == 94
    assert ratings[0].review_count == 191


def test_opencritic_treats_negative_score_as_missing() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(200, json={"topCriticScore": -1})
        )
    )
    adapter = OpenCriticAdapter(api_key="test-key", client=client)
    assert adapter.fetch_ratings(GameRef(title="Hades", opencritic_id=10181)) == []


def test_opencritic_requires_api_key() -> None:
    adapter = OpenCriticAdapter(api_key="")
    with pytest.raises(AdapterConfigError):
        adapter.fetch_ratings(GameRef(title="Hades", opencritic_id=10181))


def test_igdb_returns_critic_and_fan() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "oauth2/token" in str(request.url):
            return httpx.Response(
                200,
                json={"access_token": "token", "expires_in": 3600},
            )
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(
            200,
            json=[
                {
                    "aggregated_rating": 93.0,
                    "aggregated_rating_count": 24,
                    "rating": 89.5,
                    "rating_count": 1400,
                }
            ],
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = IGDBAdapter(client_id="id", client_secret="secret", client=client)
    ratings = adapter.fetch_ratings(GameRef(title="Hades", igdb_id=113112))
    assert [(r.audience, r.raw_score, r.review_count) for r in ratings] == [
        (RatingAudience.CRITIC, 93.0, 24),
        (RatingAudience.FAN, 89.5, 1400),
    ]
    assert all(r.source == RatingSource.IGDB for r in ratings)
