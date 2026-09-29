import pytest

from app.seed import seed


@pytest.fixture(scope="session", autouse=True)
def seed_reference_data() -> None:
    seed()
