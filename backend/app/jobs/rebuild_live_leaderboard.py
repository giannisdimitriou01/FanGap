"""Rebuild cached live leaderboard from IGDB candidate pool."""

from __future__ import annotations

from app.core.config import settings
from app.crud import leaderboard_cache as cache_crud
from app.db.session import SessionLocal
from app.services.external_ids import game_ref_from_catalog_row
from app.services.igdb_catalog import IGDBCatalogClient
from app.services.live_scores import live_divergence_stats


def rebuild_live_leaderboard() -> int:
    client = IGDBCatalogClient()
    db = SessionLocal()
    try:
        pool = client.candidate_pool(limit=settings.leaderboard_pool_size)
        ranked: list[dict] = []
        for row in pool:
            game_ref = game_ref_from_catalog_row(row, resolve_opencritic=True)
            stats = live_divergence_stats(
                game_ref,
                title=row["title"],
                cover_url=row.get("cover_url"),
                igdb_id=row["igdb_id"],
            )
            if stats["critic_score"] is None or stats["fan_score"] is None:
                continue
            ranked.append(
                {
                    "igdb_id": row["igdb_id"],
                    "title": row["title"],
                    "cover_url": row.get("cover_url"),
                    "critic_score": stats["critic_score"],
                    "fan_score": stats["fan_score"],
                    "divergence": stats["divergence"],
                }
            )
        ranked.sort(key=lambda item: item["divergence"] or 0, reverse=True)
        top = ranked[: settings.leaderboard_cache_limit]
        cache_crud.save_cache(db, {"items": top}, pool_size=len(pool))
        print(f"rebuild_live_leaderboard: stored {len(top)} entries from pool {len(pool)}")
        return len(top)
    finally:
        client.close()
        db.close()


def main() -> None:
    rebuild_live_leaderboard()


if __name__ == "__main__":
    main()
