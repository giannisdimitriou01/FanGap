"""Fetch current ratings from adapters without writing snapshots."""

from __future__ import annotations

from decimal import Decimal

from app.adapters.base import AdapterError, GameRef, RawRating
from app.models.enums import RatingAudience
from app.services.divergence_compute import NormalizedScore, compute_divergence_from_scores
from app.services.normalizer import normalize_rating
from app.services.refresh import default_adapters


def fetch_live_ratings(game_ref: GameRef, adapters: list | None = None) -> list[NormalizedScore]:
    adapters = adapters if adapters is not None else default_adapters()
    scores: list[NormalizedScore] = []
    for adapter in adapters:
        try:
            raw_ratings: list[RawRating] = adapter.fetch_ratings(game_ref)
        except AdapterError:
            continue
        for raw in raw_ratings:
            normalized = normalize_rating(raw)
            scores.append(
                NormalizedScore(
                    source=raw.source.value,
                    audience=raw.audience,
                    score=normalized,
                    review_count=raw.review_count,
                )
            )
    return scores


def live_divergence_stats(
    game_ref: GameRef,
    *,
    title: str = "",
    cover_url: str | None = None,
    igdb_id: int | None = None,
    adapters: list | None = None,
) -> dict:
    scores = fetch_live_ratings(game_ref, adapters=adapters)
    critic, fan, gap, critic_n, fan_n = compute_divergence_from_scores(scores)
    return {
        "title": title or game_ref.title,
        "cover_url": cover_url,
        "igdb_id": igdb_id if igdb_id is not None else game_ref.igdb_id,
        "critic_score": float(critic) if critic is not None else None,
        "fan_score": float(fan) if fan is not None else None,
        "divergence": float(gap) if gap is not None else None,
        "critic_samples": critic_n,
        "fan_samples": fan_n,
        "scores": [
            {
                "source": s.source,
                "audience": s.audience.value,
                "score": float(s.score),
                "review_count": s.review_count,
            }
            for s in scores
        ],
    }


def scores_from_decimals(pairs: list[tuple[str, RatingAudience, Decimal]]) -> list[NormalizedScore]:
    return [
        NormalizedScore(source=source, audience=audience, score=score)
        for source, audience, score in pairs
    ]
