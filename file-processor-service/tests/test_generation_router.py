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
                "ai_model": "gpt-4.1-nano",
                "topic_metadata": "photosynthesis",
                "note": {},
            },
        )

    assert body == {"note_task_id": "note-1"}
    assert note_task.calls[0] == {
        "ai_model": "gpt-4.1-nano",
        "extracted_text": "Topic/Text: photosynthesis",
        "folder_id": _FOLDER_ID,
        "user_id": _USER_ID,
    }
