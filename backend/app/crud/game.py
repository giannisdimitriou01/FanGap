from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Game
from app.schemas import GameCreate, GameRead, GameUpdate


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def available_genres(db: Session) -> list[str]:
    value = func.unnest(Game.genres).label("value")
    rows = db.scalars(select(value).distinct().order_by(value)).all()
    return [row for row in rows if row]


def available_platforms(db: Session) -> list[str]:
    value = func.unnest(Game.platforms).label("value")
    rows = db.scalars(select(value).distinct().order_by(value)).all()
    return [row for row in rows if row]


def list_games(
    db: Session,
    page: int,
    page_size: int,
    q: str | None = None,
    genre: str | None = None,
    platform: str | None = None,
    sort: str = "title",
) -> tuple[list[GameRead], int]:
    from app.crud.divergence import divergence_subquery

    stmt = select(Game)
    count_stmt = select(func.count()).select_from(Game)

    if q:
        pattern = f"%{_escape_like(q)}%"
        title_filter = Game.title.ilike(pattern, escape="\\")
        stmt = stmt.where(title_filter)
        count_stmt = count_stmt.where(title_filter)
    if genre:
        genre_filter = Game.genres.contains([genre])
        stmt = stmt.where(genre_filter)
        count_stmt = count_stmt.where(genre_filter)
    if platform:
        platform_filter = Game.platforms.contains([platform])
        stmt = stmt.where(platform_filter)
        count_stmt = count_stmt.where(platform_filter)

    total = db.scalar(count_stmt) or 0
    div = divergence_subquery().subquery()
    stmt = stmt.outerjoin(div, div.c.game_id == Game.id)

    if sort == "divergence":
        stmt = stmt.order_by(div.c.divergence.desc().nulls_last(), Game.title.asc())
    else:
        stmt = stmt.order_by(Game.title.asc())

    rows = db.execute(
        stmt.add_columns(div.c.critic_score, div.c.fan_score, div.c.divergence)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items: list[GameRead] = []
    for game, critic_score, fan_score, divergence in rows:
        payload = GameRead.model_validate(game)
        items.append(
            payload.model_copy(
                update={
                    "critic_score": float(critic_score) if critic_score is not None else None,
                    "fan_score": float(fan_score) if fan_score is not None else None,
                    "divergence": float(divergence) if divergence is not None else None,
                }
            )
        )
    return items, total


def create_game(db: Session, payload: GameCreate) -> Game:
    game = Game(**payload.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: int) -> Game | None:
    return db.get(Game, game_id)


def update_game(db: Session, game: Game, payload: GameUpdate) -> Game:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(game, field, value)
    db.commit()
    db.refresh(game)
    return game


def delete_game(db: Session, game: Game) -> None:
    db.delete(game)
    db.commit()
