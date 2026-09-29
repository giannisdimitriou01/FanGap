from decimal import Decimal

from app.models.enums import RatingAudience
from app.services.divergence_compute import NormalizedScore, compute_divergence_from_scores


def test_compute_divergence_averages_sources() -> None:
    scores = [
        NormalizedScore("opencritic", RatingAudience.CRITIC, Decimal("90")),
        NormalizedScore("igdb", RatingAudience.CRITIC, Decimal("94")),
        NormalizedScore("steam", RatingAudience.FAN, Decimal("96")),
        NormalizedScore("igdb", RatingAudience.FAN, Decimal("88")),
    ]
    critic, fan, gap, critic_n, fan_n = compute_divergence_from_scores(scores)
    assert critic == Decimal("92.00")
    assert fan == Decimal("92.00")
    assert gap == Decimal("0.00")
    assert critic_n == 2
    assert fan_n == 2


def test_compute_divergence_requires_both_sides() -> None:
    critic, fan, gap, critic_n, fan_n = compute_divergence_from_scores(
        [NormalizedScore("steam", RatingAudience.FAN, Decimal("80"))]
    )
    assert critic is None
    assert fan == Decimal("80.00")
    assert gap is None
