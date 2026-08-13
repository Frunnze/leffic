from collections.abc import Sequence
from typing import TypedDict

from features.study_units_generation.prompts.flashcards_prompt import (
    get_flashcards_system_prompt,
)
from features.study_units_generation.prompts.notes_prompt import (
    get_notes_system_prompt,
)
from features.study_units_generation.prompts.tests_prompt import (
    get_test_system_prompt,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import (
    save_flashcard_deck,
    save_note,
    save_test,
)
from shared.ai_manager import ai_factory
from shared.celery_app import celery_app
from shared.database import SessionLocal

_DECK_NAME = "deck_name"

FLASHCARDS_TASK = "generate_flashcards"
NOTE_TASK = "generate_note"
TEST_TASK = "generate_test"


class FlashcardsMetadata(TypedDict):
    comprehensiveness: str
    verbosity: str
    types: list[str] | None
    amount: int | None


def _generate_flashcards_task(
    *,
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    source_kind: str | None,
    source_reference: str | None,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _unused = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    with SessionLocal() as db:
        deck_id = save_flashcard_deck(
            db,
            folder_id,
            str(deck_name),
            flashcards,
            StudyUnitSource(kind=source_kind, reference=source_reference),
        )

    return {"flashcard_deck_id": deck_id, "deck_name": deck_name}


def _generate_note_task(
    *,
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    source_kind: str | None,
    source_reference: str | None,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _unused = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )
    note_name = str(note.get("note_name"))

    with SessionLocal() as db:
        note_id = save_note(
            db,
            folder_id,
            note_name,
            str(note.get("note_content")),
            StudyUnitSource(kind=source_kind, reference=source_reference),
        )

    return {"note_id": note_id, "note_name": note_name}


_TEST_ITEMS_SUFFIX = "_test_items"


def _test_items(generated: object) -> list[dict[str, object]]:
    if not isinstance(generated, Sequence) or isinstance(generated, str):
        return []

    return [item for item in generated if isinstance(item, dict)]


def _generate_test_task(
    *,
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    source_kind: str | None,
    source_reference: str | None,
    test_item_types: tuple[str, ...] = (),
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _unused = ai.get_ai_res(
        system_prompt=get_test_system_prompt(test_item_types),
        user_prompt=extracted_text,
    )
    test_name = str(test.get("test_name"))
    items = {
        key: _test_items(value)
        for key, value in test.items()
        if key.endswith(_TEST_ITEMS_SUFFIX)
    }

    with SessionLocal() as db:
        test_id = save_test(
            db,
            folder_id,
            test_name,
            items,
            StudyUnitSource(kind=source_kind, reference=source_reference),
        )

    return {"test_id": test_id, "test_name": test_name}


generate_flashcards_task = celery_app.task(
    _generate_flashcards_task, name=FLASHCARDS_TASK
)
generate_note_task = celery_app.task(_generate_note_task, name=NOTE_TASK)
generate_test_task = celery_app.task(_generate_test_task, name=TEST_TASK)
