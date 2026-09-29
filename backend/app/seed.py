"""Insert a handful of games so the list page has something to show."""

from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Game

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


def _existing_game(db, data: dict) -> Game | None:
    if data.get("steam_app_id") is not None:
        found = db.scalar(select(Game).where(Game.steam_app_id == data["steam_app_id"]))
        if found is not None:
            return found
    return db.scalar(select(Game).where(Game.title == data["title"]))


def seed() -> None:
    db = SessionLocal()
    created = 0
    updated = 0
    try:
        for data in SEED_GAMES:
            game = _existing_game(db, data)
            if game is None:
                db.add(Game(**data))
                created += 1
            else:
                for key, value in data.items():
                    setattr(game, key, value)
                updated += 1
        db.commit()
        print(f"Seed complete: {created} created, {updated} updated.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
