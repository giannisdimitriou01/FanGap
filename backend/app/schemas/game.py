from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255, examples=["Hades"])
    release_date: date | None = Field(default=None, examples=["2020-09-17"])
    genres: list[str] = Field(default_factory=list, examples=[["Action", "Roguelike"]])
    platforms: list[str] = Field(default_factory=list, examples=[["PC", "Switch"]])
    cover_url: str | None = Field(default=None, max_length=512)
    steam_app_id: int | None = Field(default=None, examples=[1145360])
    opencritic_id: int | None = Field(default=None, examples=[10181])
    igdb_id: int | None = Field(default=None, examples=[113112])


class GameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    release_date: date | None = None
    genres: list[str] | None = None
    platforms: list[str] | None = None
    cover_url: str | None = Field(default=None, max_length=512)
    steam_app_id: int | None = None
    opencritic_id: int | None = None
    igdb_id: int | None = None


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    release_date: date | None
    genres: list[str]
    platforms: list[str]
    cover_url: str | None
    steam_app_id: int | None
    opencritic_id: int | None
    igdb_id: int | None
    created_at: datetime
    updated_at: datetime
    critic_score: float | None = None
    fan_score: float | None = None
    divergence: float | None = None


class GameListResponse(BaseModel):
    items: list[GameRead]
    total: int
    page: int
    page_size: int
    genres: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
