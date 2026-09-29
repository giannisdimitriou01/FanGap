from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.adapters.base import AdapterConfigError, AdapterError
from app.crud import featured as featured_crud
from app.db.session import get_db
from app.schemas.catalog import (
    CatalogDetailRead,
    CatalogGameRead,
    CatalogListResponse,
    CatalogLiveRead,
    LiveScoreRead,
)
from app.services.external_ids import game_ref_from_catalog_row
from app.services.igdb_catalog import IGDBCatalogClient
from app.services.live_cache import cache_get, cache_set
from app.services.live_scores import live_divergence_stats

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _live_cache_key(igdb_id: int) -> str:
    return f"live:igdb:{igdb_id}"


def _build_live(row: dict, db: Session, adapters=None) -> CatalogLiveRead:
    featured = featured_crud.get_by_igdb_id(db, row["igdb_id"])
    game_ref = game_ref_from_catalog_row(row, resolve_opencritic=True)
    stats = live_divergence_stats(
        game_ref,
        title=row["title"],
        cover_url=row.get("cover_url"),
        igdb_id=row["igdb_id"],
        adapters=adapters,
    )
    return CatalogLiveRead(
        igdb_id=row["igdb_id"],
        title=stats["title"],
        cover_url=stats.get("cover_url"),
        critic_score=stats.get("critic_score"),
        fan_score=stats.get("fan_score"),
        divergence=stats.get("divergence"),
        critic_samples=stats.get("critic_samples", 0),
        fan_samples=stats.get("fan_samples", 0),
        scores=[LiveScoreRead(**item) for item in stats.get("scores", [])],
        featured_game_id=featured.id if featured else None,
    )


@router.get("/games", response_model=CatalogListResponse, summary="Search IGDB catalog")
def search_catalog(
    q: str | None = Query(None, description="Title search; empty returns popular games"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
) -> CatalogListResponse:
    client = IGDBCatalogClient()
    try:
        items, total = client.search_games(
            q or "",
            limit=page_size,
            offset=(page - 1) * page_size,
        )
    except AdapterConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AdapterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    finally:
        client.close()
    return CatalogListResponse(
        items=[CatalogGameRead(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/games/{igdb_id}", response_model=CatalogGameRead, summary="IGDB game metadata")
def catalog_game(igdb_id: int) -> CatalogGameRead:
    client = IGDBCatalogClient()
    try:
        row = client.get_game(igdb_id)
    except AdapterConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AdapterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    finally:
        client.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found in IGDB.")
    return CatalogGameRead(**row)


@router.get(
    "/games/{igdb_id}/live",
    response_model=CatalogLiveRead,
    summary="Live multi-source scores and gap",
)
def catalog_live(igdb_id: int, db: Session = Depends(get_db)) -> CatalogLiveRead:
    cached = cache_get(_live_cache_key(igdb_id))
    if cached is not None:
        return CatalogLiveRead(**cached)

    client = IGDBCatalogClient()
    try:
        row = client.get_game(igdb_id)
    except AdapterConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AdapterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    finally:
        client.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found in IGDB.")

    payload = _build_live(row, db)
    cache_set(_live_cache_key(igdb_id), payload.model_dump(mode="json"))
    return payload
