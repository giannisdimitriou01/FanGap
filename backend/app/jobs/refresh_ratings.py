"""Scheduled entrypoint: refresh featured Top 10 only."""

from app.db.session import SessionLocal
from app.crud import featured as featured_crud
from app.services.refresh import refresh_game


def main() -> None:
    db = SessionLocal()
    written = 0
    try:
        for game in featured_crud.list_featured(db):
            snapshots = refresh_game(db, game)
            written += len(snapshots)
            print(f"{game.title}: {len(snapshots)} snapshot(s)")
        print(f"refresh_ratings complete: {written} snapshot(s)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
