from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import game as game_crud
from app.db.session import get_db
from app.schemas import GameCreate, GameListResponse, GameRead, GameUpdate

router = APIRouter(prefix="/games", tags=["games"])


def _game_or_404(db: Session, game_id: int):
    game = game_crud.get_game(db, game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return game


@router.get("", response_model=GameListResponse)
def list_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> GameListResponse:
    items, total = game_crud.list_games(db, page=page, page_size=page_size)
    return GameListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameCreate, db: Session = Depends(get_db)) -> GameRead:
    try:
        return game_crud.create_game(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A game with this external ID already exists.",
        )


@router.get("/{game_id}", response_model=GameRead)
def get_game(game_id: int, db: Session = Depends(get_db)) -> GameRead:
    return _game_or_404(db, game_id)


@router.patch("/{game_id}", response_model=GameRead)
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


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, db: Session = Depends(get_db)) -> Response:
    game = _game_or_404(db, game_id)
    game_crud.delete_game(db, game)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
