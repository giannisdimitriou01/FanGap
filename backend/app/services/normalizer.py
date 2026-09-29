"""Map each source's raw score onto a common 0–100 scale."""

from decimal import Decimal, ROUND_HALF_UP

from app.adapters.base import RawRating


def normalize_score(raw_score: float, scale_max: float = 100.0) -> Decimal:
    if scale_max <= 0:
        raise ValueError("scale_max must be greater than 0")
    score = (raw_score / scale_max) * 100.0
    if score < 0 or score > 100:
        raise ValueError(f"normalized score {score} is outside 0–100")
    return Decimal(str(score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def normalize_rating(raw: RawRating) -> Decimal:
    return normalize_score(raw.raw_score, raw.scale_max)
