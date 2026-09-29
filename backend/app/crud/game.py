from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Game
from app.schemas import GameCreate


def list_games(db: Session, page: int, page_size: int) -> tuple[list[Game], int]:
    total = db.scalar(select(func.count()).select_from(Game)) or 0
    stmt = (
        select(Game)
        .order_by(Game.title.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).all())
    return items, total


def create_game(db: Session, payload: GameCreate) -> Game:
    game = Game(**payload.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game
