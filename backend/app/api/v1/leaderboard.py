from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import featured as featured_crud
from app.crud import leaderboard_cache as cache_crud
from app.db.session import get_db
from app.schemas.catalog import LiveLeaderboardEntry, LiveLeaderboardResponse

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/live", response_model=LiveLeaderboardResponse, summary="Cached live divergence ranking")
def live_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> LiveLeaderboardResponse:
    row = cache_crud.get_cache(db)
    if row is None or not row.payload.get("items"):
        return LiveLeaderboardResponse(
            items=[],
            stale=True,
            message="Live leaderboard has not been built yet. Run rebuild_live_leaderboard job.",
        )

    featured_by_igdb = {
        game.igdb_id: game.id for game in featured_crud.list_featured(db) if game.igdb_id
    }
    items: list[LiveLeaderboardEntry] = []
    for index, entry in enumerate(row.payload.get("items", [])[:limit], start=1):
        igdb_id = entry.get("igdb_id")
        items.append(
            LiveLeaderboardEntry(
                rank=index,
                igdb_id=igdb_id,
                title=entry.get("title", ""),
                cover_url=entry.get("cover_url"),
                critic_score=entry.get("critic_score"),
                fan_score=entry.get("fan_score"),
                divergence=entry.get("divergence"),
                featured_game_id=featured_by_igdb.get(igdb_id),
            )
        )
    built_at = row.built_at.isoformat() if row.built_at else None
    return LiveLeaderboardResponse(
        items=items,
        built_at=built_at,
        pool_size=row.pool_size,
        stale=False,
    )
