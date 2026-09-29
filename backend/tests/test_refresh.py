from app.adapters.base import GameRef, RawRating
from app.db.session import SessionLocal
from app.models import Game, RatingSnapshot
from app.models.enums import RatingAudience, RatingSource
from app.services.refresh import refresh_game


class FakeAdapter:
    def __init__(self, source: RatingSource, ratings: list[RawRating]) -> None:
        self.source = source
        self._ratings = ratings

    def fetch_ratings(self, game: GameRef) -> list[RawRating]:
        assert game.title
        return self._ratings


def test_refresh_writes_snapshots_from_all_three_sources() -> None:
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.title == "Hades").one()
        before = (
            db.query(RatingSnapshot)
            .filter(RatingSnapshot.game_id == game.id)
            .count()
        )
        adapters = [
            FakeAdapter(
                RatingSource.STEAM,
                [
                    RawRating(
                        source=RatingSource.STEAM,
                        audience=RatingAudience.FAN,
                        raw_score=98.0,
                        review_count=300000,
                    )
                ],
            ),
            FakeAdapter(
                RatingSource.OPENCRITIC,
                [
                    RawRating(
                        source=RatingSource.OPENCRITIC,
                        audience=RatingAudience.CRITIC,
                        raw_score=94.0,
                        review_count=191,
                    )
                ],
            ),
            FakeAdapter(
                RatingSource.IGDB,
                [
                    RawRating(
                        source=RatingSource.IGDB,
                        audience=RatingAudience.CRITIC,
                        raw_score=93.0,
                        review_count=24,
                    ),
                    RawRating(
                        source=RatingSource.IGDB,
                        audience=RatingAudience.FAN,
                        raw_score=89.5,
                        review_count=1400,
                    ),
                ],
            ),
        ]

        snapshots = refresh_game(db, game, adapters=adapters)
        sources = {snapshot.source for snapshot in snapshots}
        audiences = {(snapshot.source, snapshot.audience) for snapshot in snapshots}

        assert len(snapshots) == 4
        assert sources == {
            RatingSource.STEAM,
            RatingSource.OPENCRITIC,
            RatingSource.IGDB,
        }
        assert (RatingSource.IGDB, RatingAudience.CRITIC) in audiences
        assert (RatingSource.IGDB, RatingAudience.FAN) in audiences
        after = (
            db.query(RatingSnapshot)
            .filter(RatingSnapshot.game_id == game.id)
            .count()
        )
        assert after == before + 4
    finally:
        db.close()
