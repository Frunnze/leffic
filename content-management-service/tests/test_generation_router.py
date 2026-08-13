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

HOME_ID = uuid.UUID(USER_ID)
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"
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
    factory = in_memory_sessions()

    with factory() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.add(
            Folder(
                id=uuid.UUID(_FOLDER_ID),
                parent_id=HOME_ID,
                name="Biology",
                user_id=HOME_ID,
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


def _generate(
    client: TestClient, payload: dict[str, object]
) -> tuple[int, dict[str, object]]:
    response = client.post(
        "/generate-study-units", json=payload, headers=authorization()
    )

    return response.status_code, cast("dict[str, object]", response.json())


def test_a_note_is_queued_with_the_reviewed_text(
    client: TestClient,
) -> None:
    note_task = FakeTask("note-1")

    with mock.patch.object(router_module, "generate_note_task", note_task):
        code, body = _generate(
            client,
            {
                "text": _TEXT,
                "folder_id": _FOLDER_ID,
                "ai_model": "gpt-4.1-nano",
                "note": {},
                "source_kind": "link",
                "source_reference": "https://example.com/neurons",
            },
        )

    assert code == 200
    assert body == {"note_task_id": "note-1"}
    assert note_task.calls[0] == {
        "ai_model": "gpt-4.1-nano",
        "extracted_text": _TEXT,
        "folder_id": _FOLDER_ID,
        "source_kind": "link",
        "source_reference": "https://example.com/neurons",
    }


def test_flashcards_carry_their_type_and_amount(
    client: TestClient,
) -> None:
    flashcards_task = FakeTask("cards-1")

    with mock.patch.object(
        router_module, "generate_flashcards_task", flashcards_task
    ):
        _code, body = _generate(
            client,
            {
                "text": _TEXT,
                "folder_id": _FOLDER_ID,
                "flashcards": {"types": ["cloze"], "amount": 5},
            },
        )

    metadata = cast(
        "dict[str, object]", flashcards_task.calls[0]["flashcards_metadata"]
    )

    assert body == {"task_id": "cards-1"}
    assert metadata["types"] == ["cloze"]
    assert metadata["amount"] == 5
    assert flashcards_task.calls[0]["extracted_text"] == _TEXT
    assert flashcards_task.calls[0]["folder_id"] == _FOLDER_ID


def test_a_test_is_queued_on_its_own(client: TestClient) -> None:
    test_task = FakeTask("test-1")

    with mock.patch.object(router_module, "generate_test_task", test_task):
        _code, body = _generate(
            client,
            {"text": _TEXT, "folder_id": _FOLDER_ID, "test": {}},
        )

    assert body == {"test_task_id": "test-1"}


def test_home_resolves_to_the_callers_own_folder(
    client: TestClient,
) -> None:
    note_task = FakeTask("note-1")

    with mock.patch.object(router_module, "generate_note_task", note_task):
        _ = _generate(
            client, {"text": _TEXT, "folder_id": "home", "note": {}}
        )

    assert note_task.calls[0]["folder_id"] == USER_ID


def test_generation_without_text_is_refused(client: TestClient) -> None:
    code, body = _generate(
        client, {"text": "   ", "folder_id": _FOLDER_ID, "note": {}}
    )

    assert code == 400
    assert body["msg"] == "There is no text to generate from!"


def test_generation_without_a_folder_is_refused(
    client: TestClient,
) -> None:
    code, _body = _generate(client, {"text": _TEXT, "note": {}})

    assert code == 400


def test_asking_for_nothing_queues_nothing(client: TestClient) -> None:
    code, body = _generate(
        client, {"text": _TEXT, "folder_id": _FOLDER_ID}
    )

    assert code == 200
    assert body == {}


def test_generation_needs_a_token(client: TestClient) -> None:
    response = client.post(
        "/generate-study-units",
        json={"text": _TEXT, "folder_id": _FOLDER_ID, "note": {}},
    )

    assert response.status_code == 401

