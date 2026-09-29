from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import divergence as divergence_crud
from app.crud import featured as featured_crud
from app.crud import game as game_crud
from app.crud import ratings as ratings_crud
from app.db.session import get_db
from app.schemas import (
    CatalogDetailRead,
    CatalogGameRead,
    CatalogLiveRead,
    DivergenceListResponse,
    DivergenceRead,
    GameCreate,
    GameListResponse,
    GameRead,
    GameUpdate,
    LiveScoreRead,
    RatingListResponse,
)
from app.adapters.base import AdapterConfigError, AdapterError
from app.services.external_ids import game_ref_from_catalog_row
from app.services.igdb_catalog import IGDBCatalogClient
from app.services.live_cache import cache_get, cache_set
from app.services.live_scores import live_divergence_stats

router = APIRouter(prefix="/games", tags=["games"])


def _game_or_404(db: Session, game_id: int):
    game = game_crud.get_game(db, game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return game


def _featured_or_404(db: Session, game_id: int):
    game = _game_or_404(db, game_id)
    if game.featured_rank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History is only available for Featured Top 10 games.",
        )
    return game


@router.get(
    "",
    response_model=GameListResponse,
    summary="Featured Top 10 (snapshot history)",
    description="Postgres-backed featured games with monthly snapshot history.",
)
def list_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: Literal["title", "divergence"] = "title",
    db: Session = Depends(get_db),
) -> GameListResponse:
    items = game_crud.list_featured_games(db)
    if sort == "divergence":
        items.sort(
            key=lambda item: (item.divergence is None, -(item.divergence or 0), item.title),
        )
    else:
        items.sort(key=lambda item: item.title)
    start = (page - 1) * page_size
    end = start + page_size
    return GameListResponse(
        items=items[start:end],
        total=len(items),
        page=page,
        page_size=page_size,
        genres=[],
        platforms=[],
    )


@router.get(
    "/by-igdb/{igdb_id}",
    response_model=CatalogDetailRead,
    summary="Catalog detail with live scores and featured link",
)
def game_by_igdb(igdb_id: int, db: Session = Depends(get_db)) -> CatalogDetailRead:
    cache_key = f"live:igdb:{igdb_id}"
    cached = cache_get(cache_key)
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

    featured = featured_crud.get_by_igdb_id(db, igdb_id)
    if cached is not None:
        live = CatalogLiveRead(**cached)
    else:
        game_ref = game_ref_from_catalog_row(row, resolve_opencritic=True)
        stats = live_divergence_stats(
            game_ref,
            title=row["title"],
            cover_url=row.get("cover_url"),
            igdb_id=row["igdb_id"],
        )
        live = CatalogLiveRead(
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
        cache_set(cache_key, live.model_dump(mode="json"))

    if featured and live.featured_game_id is None:
        live = live.model_copy(update={"featured_game_id": featured.id})

    return CatalogDetailRead(
        **row,
        featured_game_id=featured.id if featured else None,
        live=live,
    )


@router.get(
    "/divergence/top",
    response_model=DivergenceListResponse,
    summary="Featured snapshot leaderboard",
    description="Top divergent games among Featured Top 10 (from stored snapshots).",
    tags=["divergence"],
)
def top_divergent(
    limit: int = Query(10, ge=1, le=10),
    db: Session = Depends(get_db),
) -> DivergenceListResponse:
    return DivergenceListResponse(items=divergence_crud.list_top_divergent(db, limit=limit))


@router.post(
    "",
    response_model=GameRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a game",
    include_in_schema=settings.enable_game_crud,
)
def create_game(payload: GameCreate, db: Session = Depends(get_db)) -> GameRead:
    if not settings.enable_game_crud:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Game CRUD is disabled.")
    try:
        return game_crud.create_game(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A game with this external ID already exists.",
        )


@router.get(
    "/{game_id}/ratings",
    response_model=RatingListResponse,
    summary="Latest ratings per source (featured only)",
    tags=["ratings"],
)
def latest_ratings(game_id: int, db: Session = Depends(get_db)) -> RatingListResponse:
    _featured_or_404(db, game_id)
    return RatingListResponse(items=ratings_crud.list_latest_ratings(db, game_id))


@router.get(
    "/{game_id}/ratings/history",
    response_model=RatingListResponse,
    summary="Full rating history (featured only)",
    description="Every snapshot for this featured game, oldest first — shaped for trend charts.",
    tags=["ratings"],
)
def rating_history(game_id: int, db: Session = Depends(get_db)) -> RatingListResponse:
    _featured_or_404(db, game_id)
    return RatingListResponse(items=ratings_crud.list_rating_history(db, game_id))


@router.get(
    "/{game_id}/divergence",
    response_model=DivergenceRead,
    summary="Critic vs fan gap for one featured game",
    tags=["divergence"],
)
def game_divergence(game_id: int, db: Session = Depends(get_db)) -> DivergenceRead:
    game = _featured_or_404(db, game_id)
    return divergence_crud.game_divergence(db, game)


@router.get("/{game_id}", response_model=GameRead, summary="Featured game detail")
def get_game(game_id: int, db: Session = Depends(get_db)) -> GameRead:
    game = _featured_or_404(db, game_id)
    stats = divergence_crud.game_divergence(db, game)
    payload = GameRead.model_validate(game)
    return payload.model_copy(
        update={
            "critic_score": float(stats.critic_score) if stats.critic_score is not None else None,
            "fan_score": float(stats.fan_score) if stats.fan_score is not None else None,
            "divergence": float(stats.divergence) if stats.divergence is not None else None,
        }
    )


@router.patch(
    "/{game_id}",
    response_model=GameRead,
    summary="Update a game",
    include_in_schema=settings.enable_game_crud,
)
def update_game(
    game_id: int,
    payload: GameUpdate,
    db: Session = Depends(get_db),
) -> GameRead:
    if not settings.enable_game_crud:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Game CRUD is disabled.")
    game = _game_or_404(db, game_id)
    try:
        return game_crud.update_game(db, game, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A game with this external ID already exists.",
        )


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a game",
    include_in_schema=settings.enable_game_crud,
)
def delete_game(game_id: int, db: Session = Depends(get_db)) -> Response:
    if not settings.enable_game_crud:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Game CRUD is disabled.")
    game = _game_or_404(db, game_id)
    game_crud.delete_game(db, game)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
