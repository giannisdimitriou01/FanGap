import os

import pytest

from app.seed import seed


@pytest.fixture(scope="session", autouse=True)
def seed_reference_data() -> None:
    os.environ["SEED_FEATURED"] = "1"
    seed()
