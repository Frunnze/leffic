import inspect
import uuid
from collections.abc import Iterator
from typing import Final, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.study_units_generation import (
    generation_router as router_module,
)
from features.study_units_generation.generation_router import (
    _queued_flashcards,
    _queued_tasks,
    _queued_test,
)
from features.study_units_generation.task_ownership import signed_task_id
from shared.database import get_db
from shared.models import Folder
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_OK: Final[int] = 200
_HOME_ID: Final[uuid.UUID] = uuid.UUID(USER_ID)
_FOLDER_ID: Final[str] = "6f1c7d4e-0000-4000-8000-000000000002"
_TEXT: Final[str] = "A neuron at rest sits near -70 mV."
_QUEUED_ID: Final[str] = "queued-1"
_RESPONSE_KEYS: Final[frozenset[str]] = frozenset({
    "note_task_id",
    "flashcard_task_ids",
    "test_task_ids",
    "flashcard_deck_id",
    "test_id",
})
_HELPER_SIGNATURES: Final[dict[str, tuple[str, ...]]] = {
    "_queued_tasks": ("request_data", "folder_id", "db"),
    "_queued_flashcards": (
        "request_data",
        "folder_id",
        "db",
        "source",
    ),
    "_queued_test": ("request_data", "folder_id", "db", "source"),
}


class RecordingQueuedTask:
    def __init__(self, task_id: str) -> None:
        self.task_id: str = task_id
        self.calls: list[dict[str, object]] = []

    def delay(self, **arguments: object) -> "RecordingQueuedTask":
        self.calls.append(arguments)

        return self

    @property
    def id(self) -> str:
        return self.task_id


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID))
        session.add(
            Folder(
                id=uuid.UUID(_FOLDER_ID),
                parent_id=_HOME_ID,
                name="Biology",
                user_id=_HOME_ID,
            )
        )
        session.commit()

    return factory


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def queued_task(
    monkeypatch: pytest.MonkeyPatch,
) -> RecordingQueuedTask:
    recorder = RecordingQueuedTask(_QUEUED_ID)

    for attribute in (
        "generate_note_task",
        "generate_flashcards_of_type_task",
        "generate_test_items_of_type_task",
    ):
        monkeypatch.setattr(router_module, attribute, recorder)

    return recorder


def _generated(
    client: TestClient, wanted: dict[str, object]
) -> dict[str, object]:
    response = client.post(
        "/generate-study-units",
        json={"text": _TEXT, "folder_id": _FOLDER_ID, **wanted},
        headers=authorization(),
    )

    assert response.status_code == _OK

    return cast("dict[str, object]", response.json())


def test_note_task_id_is_signed_with_the_target_folder(
    client: TestClient, queued_task: RecordingQueuedTask
) -> None:
    body = _generated(client, {"note": {}})

    assert body["note_task_id"] == signed_task_id(
        _QUEUED_ID, _FOLDER_ID
    )
    assert queued_task.calls[0]["folder_id"] == _FOLDER_ID


def test_flashcard_task_ids_are_each_signed(
    client: TestClient, queued_task: RecordingQueuedTask
) -> None:
    body = _generated(
        client, {"flashcards": {"types": ["basic", "cloze"]}}
    )

    assert queued_task.calls
    assert body["flashcard_task_ids"] == [
        signed_task_id(_QUEUED_ID, _FOLDER_ID)
    ] * 2


def test_test_task_ids_are_each_signed(
    client: TestClient, queued_task: RecordingQueuedTask
) -> None:
    body = _generated(
        client, {"test": {"types": ["multiple_choice", "short_answer"]}}
    )

    assert queued_task.calls
    assert body["test_task_ids"] == [
        signed_task_id(_QUEUED_ID, _FOLDER_ID)
    ] * 2


def test_response_keys_are_unchanged(
    client: TestClient, queued_task: RecordingQueuedTask
) -> None:
    assert queued_task.calls == []

    body = _generated(
        client, {"note": {}, "flashcards": {}, "test": {}}
    )

    assert frozenset(body) == _RESPONSE_KEYS
    assert body["note_task_id"] != _QUEUED_ID
    assert _QUEUED_ID not in cast(
        "list[str]", body["flashcard_task_ids"]
    )
    assert uuid.UUID(str(body["flashcard_deck_id"]))
    assert uuid.UUID(str(body["test_id"]))


def test_queued_helpers_keep_their_signatures() -> None:
    helpers = (_queued_tasks, _queued_flashcards, _queued_test)
    observed = {
        helper.__name__: tuple(
            inspect.signature(helper).parameters
        )
        for helper in helpers
    }

    assert observed == _HELPER_SIGNATURES
