from collections.abc import Iterator
from typing import cast
from unittest import mock

import jwt
import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.chatbot import chatbot as chatbot_module

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


def test_chat_answers_with_the_model_reply(client: TestClient) -> None:
    with mock.patch.object(chatbot_module, "ai_factory", FakeFactory()):
        response = client.post(
            "/chat", json={"conversation": [{"role": "user", "content": "x"}]}
        )

    body = cast("dict[str, str]", response.json())

    assert body["answer"].startswith("answered 1")


def test_generation_requires_a_token(client: TestClient) -> None:
    response = client.post("/generate-study-units", json={})

    assert response.status_code == 401


def test_generation_rejects_a_request_with_no_source(
    client: TestClient,
) -> None:
    response = client.post(
        "/generate-study-units",
        json={"folder_id": _FOLDER_ID},
        headers=_authorization(),
    )

    assert response.status_code == 400
    assert response.json()["msg"] == "Could not extract text!"
