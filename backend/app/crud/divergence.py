from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Game, RatingSnapshot
from app.models.enums import RatingAudience
from app.schemas import DivergenceRead


def _quantize(value) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def divergence_subquery():
    ranked = (
        select(
            RatingSnapshot.game_id,
            RatingSnapshot.audience,
            RatingSnapshot.score,
            func.row_number()
            .over(
                partition_by=(
                    RatingSnapshot.game_id,
                    RatingSnapshot.source,
                    RatingSnapshot.audience,
                ),
                order_by=RatingSnapshot.fetched_at.desc(),
            )
            .label("rn"),
        )
    ).subquery()
    latest = select(ranked).where(ranked.c.rn == 1).subquery()
    return (
        select(
            latest.c.game_id,
            func.avg(latest.c.score)
            .filter(latest.c.audience == RatingAudience.CRITIC.value)
            .label("critic_score"),
            func.avg(latest.c.score)
            .filter(latest.c.audience == RatingAudience.FAN.value)
            .label("fan_score"),
            func.count()
            .filter(latest.c.audience == RatingAudience.CRITIC.value)
            .label("critic_samples"),
            func.count()
            .filter(latest.c.audience == RatingAudience.FAN.value)
            .label("fan_samples"),
            func.abs(
                func.avg(latest.c.score).filter(
                    latest.c.audience == RatingAudience.CRITIC.value
                )
                - func.avg(latest.c.score).filter(
                    latest.c.audience == RatingAudience.FAN.value
                )
            ).label("divergence"),
        ).group_by(latest.c.game_id)
    )


def list_top_divergent(db: Session, limit: int = 20) -> list[DivergenceRead]:
    div = divergence_subquery().subquery()
    rows = db.execute(
        select(Game, div.c.critic_score, div.c.fan_score, div.c.divergence, div.c.critic_samples, div.c.fan_samples)
        .join(div, div.c.game_id == Game.id)
        .where(div.c.critic_score.is_not(None), div.c.fan_score.is_not(None))
        .order_by(div.c.divergence.desc(), Game.title.asc())
        .limit(limit)
    ).all()
    return [
        DivergenceRead(
            game_id=game.id,
            title=game.title,
            cover_url=game.cover_url,
            critic_score=_quantize(critic),
            fan_score=_quantize(fan),
            divergence=_quantize(gap),
            critic_samples=int(critic_n or 0),
            fan_samples=int(fan_n or 0),
        )
        for game, critic, fan, gap, critic_n, fan_n in rows
    ]


def game_divergence(db: Session, game: Game) -> DivergenceRead:
    div = divergence_subquery().subquery()
    row = db.execute(
        select(div.c.critic_score, div.c.fan_score, div.c.divergence, div.c.critic_samples, div.c.fan_samples)
        .where(div.c.game_id == game.id)
    ).first()
    if row is None:
        return DivergenceRead(
            game_id=game.id,
            title=game.title,
            cover_url=game.cover_url,
            critic_score=None,
            fan_score=None,
            divergence=None,
        )
    critic, fan, gap, critic_n, fan_n = row
    return DivergenceRead(
        game_id=game.id,
        title=game.title,
        cover_url=game.cover_url,
        critic_score=_quantize(critic),
        fan_score=_quantize(fan),
        divergence=_quantize(gap),
        critic_samples=int(critic_n or 0),
        fan_samples=int(fan_n or 0),
    )
