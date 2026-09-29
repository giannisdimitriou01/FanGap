from datetime import date

from pydantic import BaseModel, Field


class CatalogGameRead(BaseModel):
    igdb_id: int
    title: str
    release_date: date | None = None
    genres: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    cover_url: str | None = None
    steam_app_id: int | None = None


class CatalogListResponse(BaseModel):
    items: list[CatalogGameRead]
    total: int
    page: int
    page_size: int


class LiveScoreRead(BaseModel):
    source: str
    audience: str
    score: float
    review_count: int | None = None


class CatalogLiveRead(BaseModel):
    igdb_id: int
    title: str
    cover_url: str | None = None
    critic_score: float | None = None
    fan_score: float | None = None
    divergence: float | None = None
    critic_samples: int = 0
    fan_samples: int = 0
    scores: list[LiveScoreRead] = Field(default_factory=list)
    featured_game_id: int | None = None


class CatalogDetailRead(CatalogGameRead):
    featured_game_id: int | None = None
    live: CatalogLiveRead | None = None


class LiveLeaderboardEntry(BaseModel):
    igdb_id: int
    title: str
    cover_url: str | None = None
    critic_score: float | None = None
    fan_score: float | None = None
    divergence: float | None = None
    featured_game_id: int | None = None
    rank: int


class LiveLeaderboardResponse(BaseModel):
    items: list[LiveLeaderboardEntry]
    built_at: str | None = None
    pool_size: int = 0
    stale: bool = False
    message: str | None = None
