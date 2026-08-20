import uuid
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation import generation_tasks
from features.study_units_generation.generation_tasks import (
    FlashcardGenerationSettings,
    _generate_flashcards_of_type_task,
    _generate_note_task,
    _generate_test_items_of_type_task,
)
from tests.property_fakes import (
    FakeAiFactory,
    FakeAiManager,
    RecordingAppend,
    RecordingSave,
)

_NAMES = st.text(min_size=1, max_size=10)
_CARD = st.fixed_dictionaries({"front": st.text(max_size=6)})
_ITEM = st.fixed_dictionaries({"question": st.text(max_size=6)})
_FLASHCARD_TYPES = st.sampled_from(["basic", "cloze", "feynman", "list"])
_ITEM_TYPES = st.sampled_from(
    ["multiple_choice", "true_or_false", "short_answer"]
)


def _answering(payload: dict[str, object]) -> FakeAiFactory:
    return FakeAiFactory(FakeAiManager(payload))


def _asked_prompt(factory: FakeAiFactory) -> str:
    manager = factory.manager

    assert isinstance(manager, FakeAiManager)

    return manager.system_prompts[0]


@settings(max_examples=25, deadline=None)
@given(_FLASHCARD_TYPES, _NAMES, st.uuids(), st.lists(_CARD, max_size=3))
def test__generate_flashcards_of_type_task_property_reports_its_type(
    flashcard_type: str,
    deck_name: str,
    deck_id: uuid.UUID,
    cards: list[dict[str, str]],
) -> None:
    payload: dict[str, object] = {
        "deck_name": deck_name,
        f"{flashcard_type}_flashcards": cards,
        "ignored_field": "not cards",
    }
    appending = RecordingAppend(len(cards))

    with mock.patch.object(
        generation_tasks, "ai_factory", _answering(payload)
    ), mock.patch.object(
        generation_tasks, "SessionLocal"
    ), mock.patch.object(
        generation_tasks, "append_flashcards", appending
    ), mock.patch.object(generation_tasks, "name_deck_once"):
        reported = _generate_flashcards_of_type_task(
            ai_model=None,
            extracted_text="text",
            deck_id=str(deck_id),
            flashcard_type=flashcard_type,
            settings=FlashcardGenerationSettings(
                comprehensiveness="medium", verbosity="low", amount=None
            ),
        )

    assert reported == {
        "flashcard_deck_id": str(deck_id),
        "type": flashcard_type,
        "written": len(cards),
    }
    assert appending.arguments[2] == flashcard_type
    assert appending.arguments[3] == cards


@settings(max_examples=25, deadline=None)
@given(_ITEM_TYPES, _NAMES, st.uuids(), st.lists(_ITEM, max_size=3))
def test__generate_test_items_of_type_task_property_reports_its_type(
    item_type: str,
    test_name: str,
    test_id: uuid.UUID,
    items: list[dict[str, str]],
) -> None:
    payload: dict[str, object] = {
        "test_name": test_name,
        f"{item_type}_test_items": items,
        "ignored_field": "not items",
    }
    appending = RecordingAppend(len(items))
    answering = _answering(payload)

    with mock.patch.object(
        generation_tasks, "ai_factory", answering
    ), mock.patch.object(
        generation_tasks, "SessionLocal"
    ), mock.patch.object(
        generation_tasks, "append_test_items", appending
    ), mock.patch.object(generation_tasks, "name_test_once"):
        reported = _generate_test_items_of_type_task(
            ai_model=None,
            extracted_text="text",
            test_id=str(test_id),
            item_type=item_type,
            amount=9,
        )

    assert reported == {
        "test_id": str(test_id),
        "type": item_type,
        "written": len(items),
    }
    assert appending.arguments[2] == item_type
    assert appending.arguments[3] == items
    assert "Test items number: 9" in _asked_prompt(answering)


@settings(max_examples=25, deadline=None)
@given(_NAMES, st.uuids())
def test__generate_note_task_property_reports_the_note_it_saved(
    note_name: str, note_id: uuid.UUID
) -> None:
    payload: dict[str, object] = {
        "note_name": note_name,
        "note_content": "<p>body</p>",
    }
    saving = RecordingSave(str(note_id))

    with mock.patch.object(
        generation_tasks, "ai_factory", _answering(payload)
    ), mock.patch.object(
        generation_tasks, "SessionLocal"
    ), mock.patch.object(generation_tasks, "save_note", saving):
        reported = _generate_note_task(
                ai_model=None,
                extracted_text="text",
                folder_id=str(uuid.uuid4()),
                source_kind=None,
                source_reference=None,
            )

    assert reported == {"note_id": str(note_id), "note_name": note_name}
