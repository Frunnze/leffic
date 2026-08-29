import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SCHEDULER_SERVICE"] = "http://scheduler"
os.environ["REDIS_HOST"] = "localhost:6379"
os.environ["OPENAI_API_KEY"] = "test-key-never-a-real-one"
os.environ["JWT_SECRET_KEY"] = "unit-test-secret-key-value"

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import crashless_client
from tests.study_unit_access_support import StudyUnitWorld, seeded_world
from tests.support import in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def world(sessions: sessionmaker[Session]) -> StudyUnitWorld:
    return seeded_world(sessions)


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)
