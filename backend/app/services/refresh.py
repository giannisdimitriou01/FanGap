"""Fetch ratings from every adapter and append snapshot rows."""

from __future__ import annotations

import argparse
import sys

from sqlalchemy.orm import Session

from app.adapters.base import AdapterError, GameRef, RawRating
from app.adapters.igdb import IGDBAdapter
from app.adapters.opencritic import OpenCriticAdapter
from app.adapters.steam import SteamAdapter
from app.crud.game import get_game
from app.db.session import SessionLocal
from app.models import Game, RatingSnapshot
from app.services.normalizer import normalize_rating


def default_adapters() -> list:
    return [SteamAdapter(), OpenCriticAdapter(), IGDBAdapter()]


def _as_game_ref(game: Game) -> GameRef:
    return GameRef(
        title=game.title,
        steam_app_id=game.steam_app_id,
        opencritic_id=game.opencritic_id,
        igdb_id=game.igdb_id,
    )


def refresh_game(
    db: Session,
    game: Game,
    adapters: list | None = None,
) -> list[RatingSnapshot]:
    """Call each adapter, normalize, and insert a new snapshot per rating."""
    adapters = adapters if adapters is not None else default_adapters()
    game_ref = _as_game_ref(game)
    snapshots: list[RatingSnapshot] = []

    for adapter in adapters:
        try:
            raw_ratings: list[RawRating] = adapter.fetch_ratings(game_ref)
        except AdapterError as exc:
            print(f"skip {getattr(adapter, 'source', adapter)}: {exc}")
            continue

        for raw in raw_ratings:
            snapshot = RatingSnapshot(
                game_id=game.id,
                source=raw.source,
                audience=raw.audience,
                score=normalize_rating(raw),
                review_count=raw.review_count,
            )
            db.add(snapshot)
            snapshots.append(snapshot)

    db.commit()
    for snapshot in snapshots:
        db.refresh(snapshot)
    return snapshots


def refresh_game_id(game_id: int, db: Session | None = None) -> list[RatingSnapshot]:
    owns_session = db is None
    session = db or SessionLocal()
    try:
        game = get_game(session, game_id)
        if game is None:
            raise ValueError(f"Game {game_id} not found")
        return refresh_game(session, game)
    finally:
        if owns_session:
            session.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Refresh rating snapshots for a game")
    parser.add_argument("game_id", type=int)
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    snapshots = refresh_game_id(args.game_id)
    print(f"wrote {len(snapshots)} snapshot(s) for game {args.game_id}")
    for snapshot in snapshots:
        print(
            f"  {snapshot.source.value}/{snapshot.audience.value}: "
            f"{snapshot.score} (n={snapshot.review_count})"
        )


if __name__ == "__main__":
    main()
