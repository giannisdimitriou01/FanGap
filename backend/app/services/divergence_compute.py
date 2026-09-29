"""Shared critic vs fan gap math for live scores and snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.models.enums import RatingAudience


def _quantize(value: float | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class NormalizedScore:
    source: str
    audience: RatingAudience
    score: Decimal
    review_count: int | None = None


def compute_divergence_from_scores(
    scores: list[NormalizedScore],
) -> tuple[Decimal | None, Decimal | None, Decimal | None, int, int]:
    """Return critic_avg, fan_avg, gap, critic_n, fan_n."""
    critic = [float(s.score) for s in scores if s.audience == RatingAudience.CRITIC]
    fan = [float(s.score) for s in scores if s.audience == RatingAudience.FAN]
    critic_avg = sum(critic) / len(critic) if critic else None
    fan_avg = sum(fan) / len(fan) if fan else None
    if critic_avg is None or fan_avg is None:
        return (
            _quantize(critic_avg) if critic_avg is not None else None,
            _quantize(fan_avg) if fan_avg is not None else None,
            None,
            len(critic),
            len(fan),
        )
    gap = abs(critic_avg - fan_avg)
    return (
        _quantize(critic_avg),
        _quantize(fan_avg),
        _quantize(gap),
        len(critic),
        len(fan),
    )
