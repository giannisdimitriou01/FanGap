from app.models.enums import RatingAudience, RatingSource


class AdapterError(Exception):
    """Raised when an external ratings source cannot be read."""


class AdapterConfigError(AdapterError):
    """Raised when required credentials for a source are missing."""


class RawRating:
    """Predictable payload every adapter returns. The normalizer maps it to 0–100."""

    def __init__(
        self,
        *,
        source: RatingSource,
        audience: RatingAudience,
        raw_score: float,
        scale_max: float = 100.0,
        review_count: int | None = None,
    ) -> None:
        self.source = source
        self.audience = audience
        self.raw_score = raw_score
        self.scale_max = scale_max
        self.review_count = review_count

    def as_dict(self) -> dict:
        return {
            "source": self.source.value,
            "audience": self.audience.value,
            "raw_score": self.raw_score,
            "scale_max": self.scale_max,
            "review_count": self.review_count,
        }


class GameRef:
    """Minimal game identity adapters need, so they are not coupled to SQLAlchemy."""

    def __init__(
        self,
        *,
        title: str,
        steam_app_id: int | None = None,
        opencritic_id: int | None = None,
        igdb_id: int | None = None,
    ) -> None:
        self.title = title
        self.steam_app_id = steam_app_id
        self.opencritic_id = opencritic_id
        self.igdb_id = igdb_id
