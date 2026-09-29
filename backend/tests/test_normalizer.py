from decimal import Decimal

import pytest

from app.adapters.base import RawRating
from app.models.enums import RatingAudience, RatingSource
from app.services.normalizer import normalize_rating, normalize_score


def test_already_on_100_scale() -> None:
    assert normalize_score(94.0, 100.0) == Decimal("94.00")


def test_ten_point_scale() -> None:
    assert normalize_score(8.5, 10.0) == Decimal("85.00")


def test_five_point_scale() -> None:
    assert normalize_score(4.2, 5.0) == Decimal("84.00")


def test_steam_percent_positive() -> None:
    raw = RawRating(
        source=RatingSource.STEAM,
        audience=RatingAudience.FAN,
        raw_score=97.41,
        scale_max=100.0,
        review_count=200000,
    )
    assert normalize_rating(raw) == Decimal("97.41")


def test_rejects_negative_normalized_score() -> None:
    with pytest.raises(ValueError, match="outside 0–100"):
        normalize_score(-1, 100)


def test_rejects_score_above_scale() -> None:
    with pytest.raises(ValueError, match="outside 0–100"):
        normalize_score(11, 10)


def test_rejects_zero_scale() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        normalize_score(50, 0)
