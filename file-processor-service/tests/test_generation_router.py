from collections.abc import Iterator
from typing import cast
from unittest import mock

import jwt
import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.study_units_generation import (
    study_units_router as router_module,
)

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"


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


class FakeAsyncResult:
    def __init__(
        self, status: str, result: dict[str, object] | None
    ) -> None:
        super().__init__()
        self.status: str = status
        self.result: dict[str, object] | None = result

    def ready(self) -> bool:
        return self.result is not None


class FakeAi:
    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        return f"answered {len(history)} messages for {len(system_prompt)}"


class FakeFactory:
    def __init__(self) -> None:
        super().__init__()
        self.models: list[str | None] = []

    def get_ai(self, model: str | None = None) -> FakeAi:
        self.models.append(model)

        return FakeAi()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def _authorization() -> dict[str, str]:
    token = jwt.encode({"user_id": _USER_ID}, "secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


def _generate(
    client: TestClient, payload: dict[str, object]
) -> dict[str, object]:
    response = client.post(
        "/generate-study-units", json=payload, headers=_authorization()
    )

    return cast("dict[str, object]", response.json())


def test_generation_from_a_topic_queues_a_note(client: TestClient) -> None:
    note_task = FakeTask("note-1")

    with mock.patch.object(router_module, "generate_note_task", note_task):
        body = _generate(
            client,
            {
                "folder_id": _FOLDER_ID,
                "topic_metadata": "photosynthesis",
                "note": {},
            },
        )

    assert body == {"note_task_id": "note-1"}
    assert "photosynthesis" in str(note_task.calls[0]["extracted_text"])


def test_generation_from_files_queues_flashcards(client: TestClient) -> None:
    flashcards_task = FakeTask("cards-1")

    with (
        mock.patch.object(
            router_module, "text_from_files", return_value="file text"
        ),
        mock.patch.object(
            router_module, "generate_flashcards_task", flashcards_task
        ),
    ):
        body = _generate(
            client,
            {
                "folder_id": _FOLDER_ID,
                "file_metadata": [{"file_id": "f1", "extension": "pdf"}],
                "flashcards": {},
            },
        )

    assert body == {"task_id": "cards-1"}


def test_generation_from_a_link_mentions_the_source(
    client: TestClient,
) -> None:
    test_task = FakeTask("test-1")

    with (
        mock.patch.object(
            router_module, "text_from_link", return_value="link text"
        ),
        mock.patch.object(router_module, "generate_test_task", test_task),
    ):
        body = _generate(
            client,
            {
                "folder_id": _FOLDER_ID,
                "link_metadata": "https://example.com",
                "test": {},
            },
        )

    assert body == {"test_task_id": "test-1"}
    assert "source link" in str(test_task.calls[0]["extracted_text"])


def test_generation_resolves_the_home_folder(client: TestClient) -> None:
    note_task = FakeTask("note-2")

    with mock.patch.object(router_module, "generate_note_task", note_task):
        _ = _generate(
            client,
            {"folder_id": "home", "topic_metadata": "algebra", "note": {}},
        )

    assert note_task.calls[0]["folder_id"] == _USER_ID


def test_generation_rejects_a_missing_folder(client: TestClient) -> None:
    response = client.post(
        "/generate-study-units",
        json={"topic_metadata": "algebra", "note": {}},
        headers=_authorization(),
    )

    assert response.status_code == 400
