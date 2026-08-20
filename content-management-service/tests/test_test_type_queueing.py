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

_HOME_ID = uuid.UUID(USER_ID)
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"
_TEXT = "Sparta was ruled by two kings."


class FakeTaskResult:
    def __init__(self, task_id: str) -> None:
        self.id: str = task_id


class FakeTask:
    def __init__(self, task_id: str) -> None:
        self.task_id: str = task_id
        self.calls: list[dict[str, object]] = []

    def delay(self, **kwargs: object) -> FakeTaskResult:
        self.calls.append(kwargs)

        return FakeTaskResult(self.task_id)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID))
        session.add(
            Folder(
                id=uuid.UUID(_FOLDER_ID),
                parent_id=_HOME_ID,
                name="Greece",
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


def _generate_body(
    client: TestClient, payload: dict[str, object]
) -> dict[str, object]:
    response = client.post(
        "/generate-study-units", json=payload, headers=authorization()
    )

    return cast("dict[str, object]", response.json())


def _generate(client: TestClient, payload: dict[str, object]) -> None:
    _ = client.post(
        "/generate-study-units", json=payload, headers=authorization()
    )


def test_the_asked_test_types_reach_the_queued_task(
    client: TestClient,
) -> None:
    test_task = FakeTask("test-1")

    with mock.patch.object(
        router_module, "generate_test_items_of_type_task", test_task
    ):
        _generate(
            client,
            {
                "text": _TEXT,
                "folder_id": _FOLDER_ID,
                "test": {"types": ["true_or_false"]},
            },
        )

    assert test_task.calls[0]["item_type"] == "true_or_false"


def test_a_test_without_asked_types_queues_the_default(
    client: TestClient,
) -> None:
    test_task = FakeTask("test-1")

    with mock.patch.object(
        router_module, "generate_test_items_of_type_task", test_task
    ):
        _generate(client, {"text": _TEXT, "folder_id": _FOLDER_ID, "test": {}})

    assert test_task.calls[0]["item_type"] == "multiple_choice"


def test_the_text_and_folder_reach_the_queued_test_task(
    client: TestClient,
) -> None:
    test_task = FakeTask("test-1")

    with mock.patch.object(
        router_module, "generate_test_items_of_type_task", test_task
    ):
        _generate(
            client,
            {
                "text": _TEXT,
                "folder_id": _FOLDER_ID,
                "test": {"types": ["short_answer"]},
            },
        )

    queued = test_task.calls[0]

    assert queued["extracted_text"] == _TEXT
    assert queued["test_id"]


def test_flashcards_queue_one_job_for_every_asked_type(
    client: TestClient,
) -> None:
    flashcards_task = FakeTask("cards-1")

    requested_amount = 5

    with mock.patch.object(
        router_module,
        "generate_flashcards_of_type_task",
        flashcards_task,
    ):
        body = _generate_body(
            client,
            {
                "text": _TEXT,
                "folder_id": _FOLDER_ID,
                "flashcards": {
                    "types": ["cloze", "feynman"],
                    "amount": requested_amount,
                },
            },
        )

    queued = [call["flashcard_type"] for call in flashcards_task.calls]

    assert body["flashcard_task_ids"] == ["cards-1", "cards-1"]
    assert body["flashcard_deck_id"]
    assert queued == ["cloze", "feynman"]
    settings = cast(
        "dict[str, object]", flashcards_task.calls[0]["settings"]
    )

    assert settings["amount"] == requested_amount
    assert flashcards_task.calls[0]["extracted_text"] == _TEXT
    assert flashcards_task.calls[0]["deck_id"] == body["flashcard_deck_id"]
