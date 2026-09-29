"""Rotate Featured Top 10 from live leaderboard and refresh snapshots."""

from __future__ import annotations

from app.core.config import settings
from app.crud import featured as featured_crud
from app.crud import leaderboard_cache as cache_crud
from app.db.session import SessionLocal
from app.models import Game
from app.services.external_ids import game_ref_from_catalog_row, resolve_opencritic_id
from app.services.igdb_catalog import IGDBCatalogClient
from app.services.refresh import refresh_game
from app.jobs.rebuild_live_leaderboard import rebuild_live_leaderboard


def _top_entries(db) -> list[dict]:
    row = cache_crud.get_cache(db)
    if row and row.payload.get("items"):
        return row.payload["items"][: settings.featured_count]
    rebuild_live_leaderboard()
    row = cache_crud.get_cache(db)
    if row is None:
        return []
    return row.payload.get("items", [])[: settings.featured_count]


def sync_featured_top10() -> dict:
    db = SessionLocal()
    client = IGDBCatalogClient()
    try:
        targets = _top_entries(db)
        target_ids = {int(item["igdb_id"]) for item in targets if item.get("igdb_id")}

        removed = featured_crud.delete_games_not_in_igdb_ids(db, target_ids)

        added = 0
        retained = 0
        for rank, entry in enumerate(targets, start=1):
            igdb_id = int(entry["igdb_id"])
            game = featured_crud.get_by_igdb_id(db, igdb_id)
            if game is None:
                meta = client.get_game(igdb_id)
                if meta is None:
                    continue
                game = Game(
                    title=meta["title"],
                    release_date=meta.get("release_date"),
                    genres=meta.get("genres") or [],
                    platforms=meta.get("platforms") or [],
                    cover_url=meta.get("cover_url"),
                    steam_app_id=meta.get("steam_app_id"),
                    opencritic_id=resolve_opencritic_id(meta["title"]),
                    igdb_id=igdb_id,
                    featured_rank=rank,
                )
                db.add(game)
                db.commit()
                db.refresh(game)
                added += 1
            else:
                game.featured_rank = rank
                retained += 1
            refresh_game(db, game)

        db.commit()
        summary = {
            "added": added,
            "removed": len(removed),
            "retained": retained,
            "target_count": len(targets),
        }
        print(f"sync_featured_top10: {summary}")
        return summary
    finally:
        client.close()
        db.close()


def main() -> None:
    sync_featured_top10()


if __name__ == "__main__":
    main()
