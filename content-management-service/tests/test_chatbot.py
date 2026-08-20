from collections.abc import Iterator
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.chatbot import chatbot as chatbot_module


class FakeAi:
    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        return f"answered {len(history)} for {len(system_prompt)}"


class FakeFactory:
    def get_ai(self, model: str | None = None) -> FakeAi:
        _ = model

        return FakeAi()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_chat_answers_with_the_model_reply(client: TestClient) -> None:
    with mock.patch.object(chatbot_module, "ai_factory", FakeFactory()):
        response = client.post(
            "/chat",
            json={"conversation": [{"role": "user", "content": "x"}]},
        )

    body = cast("dict[str, str]", response.json())

    assert body["answer"].startswith("answered 1")


def test_chat_passes_the_whole_conversation(client: TestClient) -> None:
    conversation = [
        {"role": "user", "content": "x"},
        {"role": "assistant", "content": "y"},
        {"role": "user", "content": "z"},
    ]

    with mock.patch.object(chatbot_module, "ai_factory", FakeFactory()):
        response = client.post("/chat", json={"conversation": conversation})

    body = cast("dict[str, str]", response.json())

    assert body["answer"].startswith("answered 3")
