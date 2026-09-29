"""Insert optional featured demo data for local development."""

import os
from datetime import date, datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Game, RatingSnapshot
from app.models.enums import RatingAudience, RatingSource

SEED_FEATURED = [
    {
        "title": "Hades",
        "release_date": date(2020, 9, 17),
        "genres": ["Action", "Roguelike"],
        "platforms": ["PC", "Switch", "PS5", "Xbox"],
        "steam_app_id": 1145360,
        "opencritic_id": 10181,
        "igdb_id": 113112,
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1145360/header.jpg",
        "featured_rank": 1,
    },
]

SEED_HISTORY = {
    "Hades": [
        ("2024-01-01", RatingSource.OPENCRITIC, RatingAudience.CRITIC, 93, 120),
        ("2024-01-01", RatingSource.STEAM, RatingAudience.FAN, 96, 80000),
        ("2025-01-15", RatingSource.STEAM, RatingAudience.FAN, 98, 300000),
    ],
}


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
    if os.getenv("SEED_FEATURED", "").lower() not in {"1", "true", "yes"}:
        print("Seed skipped (set SEED_FEATURED=1 for local featured demo data).")
        return
    db = SessionLocal()
    created = 0
    history = 0
    try:
        for data in SEED_FEATURED:
            game = db.scalar(select(Game).where(Game.igdb_id == data["igdb_id"]))
            if game is None:
                game = Game(**data)
                db.add(game)
                db.flush()
                created += 1
            else:
                for key, value in data.items():
                    setattr(game, key, value)
            history += _seed_history(db, game)
        db.commit()
        print(f"Seed complete: {created} featured created, {history} history rows.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
