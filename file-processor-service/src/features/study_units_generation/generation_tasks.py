from typing import TypedDict, cast

from features.study_units_generation.content_management_client import (
    save_study_unit,
)
from features.study_units_generation.prompts.flashcards_prompt import (
    get_flashcards_system_prompt,
)
from features.study_units_generation.prompts.notes_prompt import (
    get_notes_system_prompt,
)
from features.study_units_generation.prompts.tests_prompt import (
    get_test_system_prompt,
)
from shared.ai_manager import ai_factory
from shared.celery_app import celery_app

_DECK_NAME = "deck_name"


class FlashcardsMetadata(TypedDict):
    comprehensiveness: str
    verbosity: str
    types: list[str] | None
    amount: int | None


def _generate_flashcards_task(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    answer, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    flashcards = cast("dict[str, object]", answer)
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def _generate_note_task(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    answer, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )
    note = cast("dict[str, object]", answer)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def _generate_test_task(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    answer, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )
    test = cast("dict[str, object]", answer)

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


generate_flashcards_task = celery_app.task(_generate_flashcards_task)
generate_note_task = celery_app.task(_generate_note_task)
generate_test_task = celery_app.task(_generate_test_task)
