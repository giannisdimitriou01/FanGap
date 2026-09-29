from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import game as game_crud
from app.db.session import get_db
from app.schemas import GameCreate, GameListResponse, GameRead

router = APIRouter(prefix="/games", tags=["games"])


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
