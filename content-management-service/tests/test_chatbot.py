from collections.abc import Iterator
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.chatbot import chatbot as chatbot_module
from tests.support import authorization

ONE_MESSAGE = [{"role": "user", "content": "x"}]
OK = 200
UNAUTHORIZED = 401


class RecordingAi:
    def __init__(self) -> None:
        self.histories: list[list[object]] = []

    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        self.histories.append(history)

        return f"answered {len(history)} for {len(system_prompt)}"


class RecordingFactory:
    def __init__(self) -> None:
        self.ai: RecordingAi = RecordingAi()

    def get_ai(self, model: str | None = None) -> RecordingAi:
        _ = model

        return self.ai


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def _chat_response(
    client: TestClient,
    conversation: list[dict[str, str]],
    headers: dict[str, str],
    factory: RecordingFactory,
) -> tuple[int, dict[str, str]]:
    with mock.patch.object(chatbot_module, "ai_factory", factory):
        response = client.post(
            "/chat",
            json={"conversation": conversation},
            headers=headers,
        )

    return response.status_code, cast("dict[str, str]", response.json())


def test_chat_answers_with_the_model_reply(client: TestClient) -> None:
    status_code, body = _chat_response(
        client, ONE_MESSAGE, authorization(), RecordingFactory()
    )

    assert status_code == OK
    assert body["answer"].startswith("answered 1")


def test_chat_passes_the_whole_conversation(client: TestClient) -> None:
    conversation = [
        {"role": "user", "content": "x"},
        {"role": "assistant", "content": "y"},
        {"role": "user", "content": "z"},
    ]
    factory = RecordingFactory()
    _, body = _chat_response(
        client, conversation, authorization(), factory
    )

    assert body["answer"].startswith("answered 3")
    assert factory.ai.histories == [conversation]


def test_chat_refuses_a_caller_without_a_token(
    client: TestClient,
) -> None:
    status_code, _ = _chat_response(
        client, ONE_MESSAGE, {}, RecordingFactory()
    )

    assert status_code == UNAUTHORIZED


def test_chat_never_reaches_the_model_without_a_token(
    client: TestClient,
) -> None:
    factory = RecordingFactory()
    _ = _chat_response(client, ONE_MESSAGE, {}, factory)

    assert factory.ai.histories == []
