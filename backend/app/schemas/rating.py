from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RatingAudience, RatingSource


class RatingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: RatingSource
    audience: RatingAudience
    score: Decimal
    review_count: int | None
    fetched_at: datetime


class RatingListResponse(BaseModel):
    items: list[RatingRead]


class DivergenceRead(BaseModel):
    game_id: int
    title: str
    cover_url: str | None = None
    critic_score: Decimal | None
    fan_score: Decimal | None
    divergence: Decimal | None
    critic_samples: int = 0
    fan_samples: int = 0


class DivergenceListResponse(BaseModel):
    items: list[DivergenceRead]
