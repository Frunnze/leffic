import json
from unittest import mock

import pytest
import requests

from features.study_units_generation import generation_tasks
from features.study_units_generation.generation_tasks import (
    FlashcardsMetadata,
)

_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"
_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_TEXT = "some study material"
_METADATA: FlashcardsMetadata = {
    "comprehensiveness": "medium",
    "verbosity": "low",
    "types": ["cloze"],
    "amount": 5,
}


class FakeResponse:
    def __init__(
        self, payload: dict[str, object], status_code: int = 200
    ) -> None:
        super().__init__()
        self.text: str = json.dumps(payload)
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


class FakeAi:
    def __init__(self, answer: object) -> None:
        super().__init__()
        self.answer: object = answer
        self.prompts: list[str] = []

    def get_ai_res(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[object, float | None]:
        self.prompts.append(system_prompt)
        self.prompts.append(user_prompt)

        return self.answer, None


class FakeFactory:
    def __init__(self, ai: FakeAi) -> None:
        super().__init__()
        self.ai: FakeAi = ai
        self.models: list[str | None] = []

    def get_ai(self, model: str | None = None) -> FakeAi:
        self.models.append(model)

        return self.ai


def _use_ai(answer: object) -> FakeFactory:
    factory = FakeFactory(FakeAi(answer))
    _ = mock.patch.object(generation_tasks, "ai_factory", factory).start()

    return factory


@pytest.fixture(autouse=True)
def stop_patches() -> None:
    mock.patch.stopall()


def test_generating_a_note_saves_it_and_returns_the_id() -> None:
    factory = _use_ai({"note_content": "<p>x</p>", "note_name": "Cells"})

    with mock.patch.object(
        generation_tasks, "save_study_unit", return_value={"note_id": "n1"}
    ) as save:
        result = generation_tasks._generate_note_task(
            "gpt-4.1-nano", _TEXT, _FOLDER_ID, _USER_ID
        )

    assert factory.models == ["gpt-4.1-nano"]
    assert "expert in creating notes" in factory.ai.prompts[0]
    assert factory.ai.prompts[1] == _TEXT

    assert result == {"note_id": "n1", "note_name": "Cells"}
    assert save.call_args.args[0] == "/save-note"
    assert save.call_args.args[1] == {
        "note_content": "<p>x</p>",
        "note_name": "Cells",
        "folder_id": _FOLDER_ID,
        "user_id": _USER_ID,
    }


def test_generating_a_test_saves_it_and_returns_the_id() -> None:
    factory = _use_ai(
        {"multiple_choice_test_items": [{"question": "q"}], "test_name": "T"}
    )

    with mock.patch.object(
        generation_tasks, "save_study_unit", return_value={"test_id": "t1"}
    ) as save:
        result = generation_tasks._generate_test_task(
            "gpt-4.1-nano", _TEXT, _FOLDER_ID, _USER_ID
        )

    assert factory.models == ["gpt-4.1-nano"]
    assert "expert in creating tests" in factory.ai.prompts[0]
    assert factory.ai.prompts[1] == _TEXT

    assert result == {"test_id": "t1", "test_name": "T"}
    assert save.call_args.args[0] == "/save-test"
    assert save.call_args.args[1] == {
        "test_items": [{"question": "q"}],
        "test_name": "T",
        "folder_id": _FOLDER_ID,
        "user_id": _USER_ID,
    }
