from unittest import mock

import pytest
import requests

from features.study_units_generation import generation_tasks
from features.study_units_generation.content_management_client import (
    save_study_unit,
)
from features.study_units_generation.generation_tasks import (
    FlashcardsMetadata,
)
from shared.settings import CONTENT_MANAGEMENT_SERVICE

_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"
_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_TEXT = "some study material"
_METADATA: FlashcardsMetadata = {
    "comprehensiveness": "medium",
    "verbosity": "low",
    "types": ["basic"],
    "amount": 5,
}


class FakeResponse:
    def __init__(
        self, payload: dict[str, object], status_code: int = 200
    ) -> None:
        super().__init__()
        self.payload: dict[str, object] = payload
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self) -> dict[str, object]:
        return self.payload


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


def test_save_study_unit_posts_to_content_management() -> None:
    with mock.patch.object(
        requests, "post", return_value=FakeResponse({"note_id": "n1"})
    ) as post:
        saved = save_study_unit("/save-note", {"a": 1})

    assert saved == {"note_id": "n1"}
    assert post.call_args.kwargs["json"] == {"a": 1}


def test_save_study_unit_raises_on_an_error_status() -> None:
    with (
        mock.patch.object(
            requests, "post", return_value=FakeResponse({}, 500)
        ),
        pytest.raises(requests.HTTPError),
    ):
        _ = save_study_unit("/save-note", {})


def test_save_study_unit_targets_the_configured_service() -> None:
    with mock.patch.object(
        requests, "post", return_value=FakeResponse({})
    ) as post:
        _ = save_study_unit("/save-test", {})

    expected = f"{CONTENT_MANAGEMENT_SERVICE}/save-test"

    assert post.call_args.kwargs["url"] == expected


def test_generating_flashcards_saves_them_and_returns_the_deck() -> None:
    answer = {"deck_name": "Biology", "basic_flashcards": [{"front": "q"}]}
    factory = _use_ai(answer)

    with mock.patch.object(
        generation_tasks,
        "save_study_unit",
        return_value={"flashcard_deck_id": "deck-1"},
    ) as save:
        result = generation_tasks._generate_flashcards_task(
            "gpt-4.1-nano", _TEXT, _METADATA, _FOLDER_ID, _USER_ID
        )

    assert result == {
        "flashcard_deck_id": "deck-1",
        "deck_name": "Biology",
    }
    assert save.call_args.args[0] == "/save-flashcards"
    assert factory.models == ["gpt-4.1-nano"]


def test_generating_flashcards_strips_the_deck_name_from_the_payload() -> None:
    answer: dict[str, object] = {
        "deck_name": "Biology",
        "basic_flashcards": [],
    }
    _ = _use_ai(answer)

    with mock.patch.object(
        generation_tasks, "save_study_unit", return_value={}
    ) as save:
        _ = generation_tasks._generate_flashcards_task(
            None, _TEXT, _METADATA, _FOLDER_ID, _USER_ID
        )

    assert "deck_name" not in save.call_args.args[1]["flashcards"]


def test_generating_flashcards_handles_missing_types() -> None:
    metadata: FlashcardsMetadata = {
        "comprehensiveness": "high",
        "verbosity": "high",
        "types": None,
        "amount": None,
    }
    factory = _use_ai({"deck_name": "Deck"})

    with mock.patch.object(
        generation_tasks, "save_study_unit", return_value={}
    ):
        _ = generation_tasks._generate_flashcards_task(
            None, _TEXT, metadata, _FOLDER_ID, _USER_ID
        )

    assert "Comprehensiveness: high" in factory.ai.prompts[0]


def test_generating_a_note_saves_it_and_returns_the_id() -> None:
    _ = _use_ai({"note_content": "<p>x</p>", "note_name": "Cells"})

    with mock.patch.object(
        generation_tasks, "save_study_unit", return_value={"note_id": "n1"}
    ) as save:
        result = generation_tasks._generate_note_task(
            None, _TEXT, _FOLDER_ID, _USER_ID
        )

    assert result == {"note_id": "n1", "note_name": "Cells"}
    assert save.call_args.args[0] == "/save-note"


def test_generating_a_test_saves_it_and_returns_the_id() -> None:
    _ = _use_ai(
        {"multiple_choice_test_items": [{"question": "q"}], "test_name": "T"}
    )

    with mock.patch.object(
        generation_tasks, "save_study_unit", return_value={"test_id": "t1"}
    ) as save:
        result = generation_tasks._generate_test_task(
            None, _TEXT, _FOLDER_ID, _USER_ID
        )

    assert result == {"test_id": "t1", "test_name": "T"}
    assert save.call_args.args[0] == "/save-test"
