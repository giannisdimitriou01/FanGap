"""Insert games plus a short rating history so charts and divergence have data."""

from datetime import date, datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Game, RatingSnapshot
from app.models.enums import RatingAudience, RatingSource

SEED_GAMES = [
    {
        "title": "Hades",
        "release_date": date(2020, 9, 17),
        "genres": ["Action", "Roguelike"],
        "platforms": ["PC", "Switch", "PS5", "Xbox"],
        "steam_app_id": 1145360,
        "opencritic_id": 10181,
        "igdb_id": 113112,
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1145360/header.jpg",
    },
    {
        "title": "Cyberpunk 2077",
        "release_date": date(2020, 12, 10),
        "genres": ["RPG", "Action"],
        "platforms": ["PC", "PS5", "Xbox"],
        "steam_app_id": 1091500,
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
    },
    {
        "title": "Elden Ring",
        "release_date": date(2022, 2, 25),
        "genres": ["Action", "RPG"],
        "platforms": ["PC", "PS5", "Xbox"],
        "steam_app_id": 1245620,
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/header.jpg",
    },
    {
        "title": "Starfield",
        "release_date": date(2023, 9, 6),
        "genres": ["RPG", "Open World"],
        "platforms": ["PC", "Xbox"],
        "steam_app_id": 1716740,
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1716740/header.jpg",
    },
    {
        "title": "Baldur's Gate 3",
        "release_date": date(2023, 8, 3),
        "genres": ["RPG", "Strategy"],
        "platforms": ["PC", "PS5", "Xbox"],
        "steam_app_id": 1086940,
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1086940/header.jpg",
    },
]

# Historical points so the trend chart and leaderboard are visible before live keys exist.
SEED_HISTORY = {
    "Hades": [
        ("2021-03-01", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 93, 120),
        ("2021-03-01", RatingSource.STEAM, RatingAudience.FAN, 96, 80000),
        ("2023-06-01", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 94, 180),
        ("2023-06-01", RatingSource.STEAM, RatingAudience.FAN, 97, 180000),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.CRITIC, 93, 24),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.FAN, 90, 1400),
        ("2025-01-15", RatingSource.STEAM, RatingAudience.FAN, 98, 300000),
    ],
    "Cyberpunk 2077": [
        ("2020-12-15", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 76, 90),
        ("2020-12-15", RatingSource.STEAM, RatingAudience.FAN, 58, 200000),
        ("2022-09-01", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 78, 140),
        ("2022-09-01", RatingSource.STEAM, RatingAudience.FAN, 79, 400000),
        ("2025-01-15", RatingSource.STEAM, RatingAudience.FAN, 89, 650000),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.CRITIC, 77, 40),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.FAN, 86, 8000),
    ],
    "Elden Ring": [
        ("2022-03-01", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 95, 100),
        ("2022-03-01", RatingSource.STEAM, RatingAudience.FAN, 94, 150000),
        ("2025-01-15", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 96, 160),
        ("2025-01-15", RatingSource.STEAM, RatingAudience.FAN, 93, 500000),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.CRITIC, 95, 50),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.FAN, 92, 9000),
    ],
    "Starfield": [
        ("2023-09-10", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 83, 80),
        ("2023-09-10", RatingSource.STEAM, RatingAudience.FAN, 71, 90000),
        ("2025-01-15", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 85, 120),
        ("2025-01-15", RatingSource.STEAM, RatingAudience.FAN, 67, 180000),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.CRITIC, 84, 30),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.FAN, 68, 4000),
    ],
    "Baldur's Gate 3": [
        ("2023-08-10", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 96, 90),
        ("2023-08-10", RatingSource.STEAM, RatingAudience.FAN, 96, 120000),
        ("2025-01-15", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 97, 150),
        ("2025-01-15", RatingSource.STEAM, RatingAudience.FAN, 96, 400000),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.CRITIC, 96, 45),
        ("2025-01-15", RatingSource.IGDB, RatingAudience.FAN, 95, 7000),
    ],
}


def _existing_game(db, data: dict) -> Game | None:
    if data.get("steam_app_id") is not None:
        found = db.scalar(select(Game).where(Game.steam_app_id == data["steam_app_id"]))
        if found is not None:
            return found
    return db.scalar(select(Game).where(Game.title == data["title"]))


def _seed_history(db, game: Game) -> int:
    added = 0
    for day, source, audience, score, reviews in SEED_HISTORY.get(game.title, []):
        fetched_at = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
        exists = db.scalar(
            select(RatingSnapshot.id).where(
                RatingSnapshot.game_id == game.id,
                RatingSnapshot.source == source,
                RatingSnapshot.audience == audience,
                RatingSnapshot.fetched_at == fetched_at,
            )
        )
        if exists is not None:
            continue
        db.add(
            RatingSnapshot(
                game_id=game.id,
                source=source,
                audience=audience,
                score=score,
                review_count=reviews,
                fetched_at=fetched_at,
            )
        )
        added += 1
    return added


def seed() -> None:
    db = SessionLocal()
    created = 0
    updated = 0
    history = 0
    try:
        for data in SEED_GAMES:
            game = _existing_game(db, data)
            if game is None:
                game = Game(**data)
                db.add(game)
                db.flush()
                created += 1
            else:
                for key, value in data.items():
                    setattr(game, key, value)
                updated += 1
            history += _seed_history(db, game)
        db.commit()
        print(f"Seed complete: {created} created, {updated} updated, {history} history rows.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
