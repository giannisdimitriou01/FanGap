from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    release_date: date | None = None
    genres: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    cover_url: str | None = Field(default=None, max_length=512)
    steam_app_id: int | None = None
    opencritic_id: int | None = None
    igdb_id: int | None = None


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


class GameListResponse(BaseModel):
    items: list[GameRead]
    total: int
    page: int
    page_size: int
