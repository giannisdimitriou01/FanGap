from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import divergence as divergence_crud
from app.crud import game as game_crud
from app.crud import ratings as ratings_crud
from app.db.session import get_db
from app.schemas import (
    DivergenceListResponse,
    DivergenceRead,
    GameCreate,
    GameListResponse,
    GameRead,
    GameUpdate,
    RatingListResponse,
)

router = APIRouter(prefix="/games", tags=["games"])


def _game_or_404(db: Session, game_id: int):
    game = game_crud.get_game(db, game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return game


@router.get(
    "",
    response_model=GameListResponse,
    summary="List games",
    description="Paginated game list. Filter by title, genre, or platform; sort by title or divergence.",
)
def list_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, description="Case-insensitive title search"),
    genre: str | None = Query(None),
    platform: str | None = Query(None),
    sort: Literal["title", "divergence"] = "title",
    db: Session = Depends(get_db),
) -> GameListResponse:
    items, total = game_crud.list_games(
        db,
        page=page,
        page_size=page_size,
        q=q,
        genre=genre,
        platform=platform,
        sort=sort,
    )
    return GameListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        genres=game_crud.available_genres(db),
        platforms=game_crud.available_platforms(db),
    )


@router.get(
    "/divergence/top",
    response_model=DivergenceListResponse,
    summary="Most divergent games",
    description="Leaderboard of games with the largest gap between latest critic and fan scores.",
    tags=["divergence"],
)
def top_divergent(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> DivergenceListResponse:
    return DivergenceListResponse(items=divergence_crud.list_top_divergent(db, limit=limit))


@router.post(
    "",
    response_model=GameRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a game",
)
def create_game(payload: GameCreate, db: Session = Depends(get_db)) -> GameRead:
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
    summary="Latest ratings per source",
    tags=["ratings"],
)
def latest_ratings(game_id: int, db: Session = Depends(get_db)) -> RatingListResponse:
    _game_or_404(db, game_id)
    return RatingListResponse(items=ratings_crud.list_latest_ratings(db, game_id))


@router.get(
    "/{game_id}/ratings/history",
    response_model=RatingListResponse,
    summary="Full rating history",
    description="Every snapshot for this game, oldest first — shaped for trend charts.",
    tags=["ratings"],
)
def rating_history(game_id: int, db: Session = Depends(get_db)) -> RatingListResponse:
    _game_or_404(db, game_id)
    return RatingListResponse(items=ratings_crud.list_rating_history(db, game_id))


@router.get(
    "/{game_id}/divergence",
    response_model=DivergenceRead,
    summary="Critic vs fan gap for one game",
    tags=["divergence"],
)
def game_divergence(game_id: int, db: Session = Depends(get_db)) -> DivergenceRead:
    game = _game_or_404(db, game_id)
    return divergence_crud.game_divergence(db, game)


@router.get("/{game_id}", response_model=GameRead, summary="Game detail")
def get_game(game_id: int, db: Session = Depends(get_db)) -> GameRead:
    game = _game_or_404(db, game_id)
    stats = divergence_crud.game_divergence(db, game)
    payload = GameRead.model_validate(game)
    return payload.model_copy(
        update={
            "critic_score": float(stats.critic_score) if stats.critic_score is not None else None,
            "fan_score": float(stats.fan_score) if stats.fan_score is not None else None,
            "divergence": float(stats.divergence) if stats.divergence is not None else None,
        }
    )


@router.patch("/{game_id}", response_model=GameRead, summary="Update a game")
def update_game(
    game_id: int,
    payload: GameUpdate,
    db: Session = Depends(get_db),
) -> GameRead:
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
)
def delete_game(game_id: int, db: Session = Depends(get_db)) -> Response:
    game = _game_or_404(db, game_id)
    game_crud.delete_game(db, game)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
