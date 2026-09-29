from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Game


def get_by_igdb_id(db: Session, igdb_id: int) -> Game | None:
    return db.scalar(select(Game).where(Game.igdb_id == igdb_id))


def list_featured(db: Session) -> list[Game]:
    return list(
        db.scalars(
            select(Game)
            .where(Game.featured_rank.is_not(None))
            .order_by(Game.featured_rank.asc())
        ).all()
    )


def delete_games_not_in_igdb_ids(db: Session, keep_igdb_ids: set[int]) -> list[int]:
    removed: list[int] = []
    for game in db.scalars(select(Game)).all():
        if game.igdb_id is None or game.igdb_id not in keep_igdb_ids:
            removed.append(game.id)
            db.delete(game)
    db.commit()
    return removed
