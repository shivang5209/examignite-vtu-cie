from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.db import Base, SessionLocal, engine
from app.services.db_seed import seed_demo_data


@pytest.fixture(scope="session", autouse=True)
def bootstrap_test_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_demo_data(session)
