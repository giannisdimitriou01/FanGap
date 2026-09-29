from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RatingAudience, RatingSource


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RatingSnapshot(Base):
    __tablename__ = "rating_snapshots"
    __table_args__ = (
        CheckConstraint(
            "score >= 0 AND score <= 100",
            name="ck_rating_snapshots_score_range",
        ),
        Index("ix_rating_snapshots_game_fetched", "game_id", "fetched_at"),
        Index(
            "ix_rating_snapshots_game_source_audience",
            "game_id",
            "source",
            "audience",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[RatingSource] = mapped_column(
        Enum(
            RatingSource,
            native_enum=False,
            length=32,
            values_callable=lambda members: [member.value for member in members],
        ),
        nullable=False,
    )
    audience: Mapped[RatingAudience] = mapped_column(
        Enum(
            RatingAudience,
            native_enum=False,
            length=32,
            values_callable=lambda members: [member.value for member in members],
        ),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    game: Mapped["Game"] = relationship(back_populates="snapshots")
