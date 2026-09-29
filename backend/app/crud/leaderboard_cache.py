from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LeaderboardCache


def get_cache(db: Session) -> LeaderboardCache | None:
    return db.get(LeaderboardCache, 1)


def save_cache(db: Session, payload: dict, pool_size: int) -> LeaderboardCache:
    row = db.get(LeaderboardCache, 1)
    if row is None:
        row = LeaderboardCache(id=1, payload=payload, pool_size=pool_size)
        db.add(row)
    else:
        row.payload = payload
        row.pool_size = pool_size
        row.built_at = datetime.now().astimezone()
    db.commit()
    db.refresh(row)
    return row
