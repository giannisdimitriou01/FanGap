from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RatingSnapshot


def list_latest_ratings(db: Session, game_id: int) -> list[RatingSnapshot]:
    ranked = (
        select(
            RatingSnapshot.id,
            func.row_number()
            .over(
                partition_by=(RatingSnapshot.source, RatingSnapshot.audience),
                order_by=RatingSnapshot.fetched_at.desc(),
            )
            .label("rn"),
        ).where(RatingSnapshot.game_id == game_id)
    ).subquery()
    ids = list(db.scalars(select(ranked.c.id).where(ranked.c.rn == 1)).all())
    if not ids:
        return []
    return list(
        db.scalars(
            select(RatingSnapshot)
            .where(RatingSnapshot.id.in_(ids))
            .order_by(RatingSnapshot.source, RatingSnapshot.audience)
        ).all()
    )


def list_rating_history(db: Session, game_id: int) -> list[RatingSnapshot]:
    return list(
        db.scalars(
            select(RatingSnapshot)
            .where(RatingSnapshot.game_id == game_id)
            .order_by(RatingSnapshot.fetched_at.asc(), RatingSnapshot.id.asc())
        ).all()
    )
