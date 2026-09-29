"""Scheduled entrypoint: refresh every game in the database."""

from app.services.refresh import refresh_all


def main() -> None:
    written = refresh_all()
    print(f"refresh_ratings complete: {written} snapshot(s)")


if __name__ == "__main__":
    main()
