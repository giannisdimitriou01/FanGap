from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    opencritic_rapidapi_key: str = ""
    igdb_client_id: str = ""
    igdb_client_secret: str = ""
    live_cache_ttl_seconds: int = 3600
    leaderboard_pool_size: int = 150
    leaderboard_cache_limit: int = 50
    featured_count: int = 10
    enable_game_crud: bool = False


settings = Settings()
