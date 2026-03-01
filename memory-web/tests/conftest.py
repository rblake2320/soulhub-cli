"""
Test fixtures for MemoryWeb.
Uses an in-memory SQLite for unit tests; PostgreSQL integration tests
are gated behind MEMORYWEB_TEST_PG=1.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Patch settings before importing app modules
os.environ.setdefault("MW_DATABASE_URL", "sqlite:///./test_memoryweb.db")
os.environ.setdefault("MW_REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("MW_CELERY_BROKER_URL", "redis://localhost:6379/15")
os.environ.setdefault("MW_CELERY_RESULT_BACKEND", "redis://localhost:6379/15")

from app.database import Base
from app.main import app
from app.deps import get_db


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///./test_memoryweb.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    Session = sessionmaker(bind=test_engine)
    db = Session()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
