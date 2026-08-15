import uuid
from typing import cast
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation import generation_tasks
from features.study_units_generation.generation_tasks import (
    FlashcardsMetadata,
    _generate_flashcards_task,
    _generate_note_task,
    _generate_test_task,
    _test_items,
)
from tests.property_fakes import FakeAiFactory, FakeAiManager, RecordingSave

_METADATA: FlashcardsMetadata = {
    "comprehensiveness": "medium",
    "verbosity": "low",
    "types": ["basic"],
    "amount": None,
}
_NAMES = st.text(min_size=1, max_size=10)
_ITEM = st.fixed_dictionaries({"question": st.text(max_size=6)})


def _answering(payload: dict[str, object]) -> FakeAiFactory:
    return FakeAiFactory(FakeAiManager(payload))


@settings(max_examples=50)
@given(
    st.one_of(
        st.lists(st.one_of(_ITEM, st.integers(), st.none()), max_size=4),
        st.text(max_size=5),
        st.integers(),
        st.none(),
    )
)
def test__test_items_property_keeps_exactly_the_mappings(
    generated: object,
) -> None:
    kept = _test_items(generated)

    if isinstance(generated, list):
        expected: list[object] = [
            item
            for item in cast("list[object]", generated)
            if isinstance(item, dict)
        ]

        assert list(kept) == expected
    else:
        assert kept == []


@settings(max_examples=25, deadline=None)
@given(_NAMES, st.uuids())
def test__generate_flashcards_task_property_reports_the_deck_it_saved(
    deck_name: str, deck_id: uuid.UUID
) -> None:
    payload: dict[str, object] = {
        "deck_name": deck_name,
        "basic_flashcards": [],
    }
    saving = RecordingSave(str(deck_id))

    with mock.patch.object(
        generation_tasks, "ai_factory", _answering(payload)
    ), mock.patch.object(generation_tasks, "SessionLocal"), mock.patch.object(
        generation_tasks, "save_flashcard_deck", saving
    ):
        reported = _generate_flashcards_task(
            ai_model=None,
            extracted_text="text",
            flashcards_metadata=_METADATA,
            folder_id=str(uuid.uuid4()),
            source_kind=None,
            source_reference=None,
        )

    assert reported == {
        "flashcard_deck_id": str(deck_id),
        "deck_name": deck_name,
    }


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
    ), mock.patch.object(generation_tasks, "SessionLocal"):
        with mock.patch.object(generation_tasks, "save_note", saving):
            reported = _generate_note_task(
                ai_model=None,
                extracted_text="text",
                folder_id=str(uuid.uuid4()),
                source_kind=None,
                source_reference=None,
            )

    assert reported == {"note_id": str(note_id), "note_name": note_name}


@settings(max_examples=25, deadline=None)
@given(_NAMES, st.uuids(), st.lists(_ITEM, max_size=3))
def test__generate_test_task_property_reports_the_test_it_saved(
    test_name: str, test_id: uuid.UUID, items: list[dict[str, str]]
) -> None:
    payload: dict[str, object] = {
        "test_name": test_name,
        "multiple_choice_test_items": items,
        "ignored_field": "not items",
    }
    saving = RecordingSave(str(test_id))

    with mock.patch.object(
        generation_tasks, "ai_factory", _answering(payload)
    ), mock.patch.object(generation_tasks, "SessionLocal"):
        with mock.patch.object(generation_tasks, "save_test", saving):
            reported = _generate_test_task(
                ai_model=None,
                extracted_text="text",
                folder_id=str(uuid.uuid4()),
                source_kind=None,
                source_reference=None,
            )

    assert reported == {"test_id": str(test_id), "test_name": test_name}
    assert saving.arguments[3] == {"multiple_choice_test_items": items}
