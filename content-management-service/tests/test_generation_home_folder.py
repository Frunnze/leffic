import uuid
from collections.abc import Iterator
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.study_units_generation import (
    generation_router as router_module,
)
from shared.database import get_db
from shared.models import Folder
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_OK = 200

HOME_ID = uuid.UUID(USER_ID)
_TEXT = "A neuron at rest sits near -70 mV."


class FakeTaskResult:
    def __init__(self, task_id: str) -> None:
        super().__init__()
        self.id: str = task_id


class FakeTask:
    def __init__(self, task_id: str) -> None:
        super().__init__()
        self.task_id: str = task_id
        self.calls: list[dict[str, object]] = []

    def delay(self, **kwargs: object) -> FakeTaskResult:
        self.calls.append(kwargs)

        return FakeTaskResult(self.task_id)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def test_generating_into_home_creates_it_when_it_is_missing(
    sessions: sessionmaker[Session], client: TestClient
) -> None:
    note_task = FakeTask("note-1")

    with mock.patch.object(router_module, "generate_note_task", note_task):
        response = client.post(
            "/generate-study-units",
            json={"text": _TEXT, "folder_id": "home", "note": {}},
            headers=authorization(),
        )

    with sessions() as session:
        home = session.query(Folder).filter_by(id=HOME_ID).one()

    assert response.status_code == _OK
    assert cast("dict[str, str]", response.json()) == {
        "note_task_id": "note-1"
    }
    assert home.name == "Home"
    assert note_task.calls[0]["folder_id"] == USER_ID
