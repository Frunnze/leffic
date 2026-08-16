from features.study_units_generation.assessment_writer import (
    append_test_items,
    name_test_once,
)
from features.study_units_generation.celery_app import celery_app
from features.study_units_generation.flashcard_deck_writer import (
    append_flashcards,
    name_deck_once,
)
from features.study_units_generation.prompts.prompt_file import (
    assessment_item_values,
    flashcard_values,
    rendered_prompt,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_types import (
    NOTE_PROMPT_FILE,
    study_unit_type,
)
from features.study_units_generation.study_unit_writer import save_note
from shared.ai_manager import ai_factory
from shared.database import SessionLocal

_DECK_NAME = "deck_name"
_TEST_NAME = "test_name"

FLASHCARDS_TASK = "generate_flashcards_of_type"
NOTE_TASK = "generate_note"
TEST_TASK = "generate_test_items_of_type"


def _generate_flashcards_of_type_task(
    *,
    ai_model: str | None,
    extracted_text: str,
    deck_id: str,
    flashcard_type: str,
    comprehensiveness: str,
    verbosity: str,
    amount: int | None,
) -> dict[str, object]:
    unit_type = study_unit_type(flashcard_type)
    ai = ai_factory.get_ai(ai_model)
    generated, _unused = ai.get_ai_res(
        system_prompt=rendered_prompt(
            unit_type.prompt_file,
            flashcard_values(comprehensiveness, verbosity, amount),
        ),
        user_prompt=extracted_text,
    )

    with SessionLocal() as db:
        written = append_flashcards(
            db, deck_id, unit_type.name, generated.get(unit_type.result_key)
        )
        _ = name_deck_once(db, deck_id, str(generated.get(_DECK_NAME)))

    return {
        "flashcard_deck_id": deck_id,
        "type": unit_type.name,
        "written": written,
    }


def _generate_test_items_of_type_task(
    *,
    ai_model: str | None,
    extracted_text: str,
    test_id: str,
    item_type: str,
    amount: int | None,
) -> dict[str, object]:
    unit_type = study_unit_type(item_type)
    ai = ai_factory.get_ai(ai_model)
    generated, _unused = ai.get_ai_res(
        system_prompt=rendered_prompt(
            unit_type.prompt_file, assessment_item_values(amount)
        ),
        user_prompt=extracted_text,
    )

    with SessionLocal() as db:
        written = append_test_items(
            db, test_id, unit_type.name, generated.get(unit_type.result_key)
        )
        _ = name_test_once(db, test_id, str(generated.get(_TEST_NAME)))

    return {
        "test_id": test_id,
        "type": unit_type.name,
        "written": written,
    }


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
        system_prompt=rendered_prompt(NOTE_PROMPT_FILE, {}),
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


generate_flashcards_of_type_task = celery_app.task(
    _generate_flashcards_of_type_task, name=FLASHCARDS_TASK
)
generate_test_items_of_type_task = celery_app.task(
    _generate_test_items_of_type_task, name=TEST_TASK
)
generate_note_task = celery_app.task(_generate_note_task, name=NOTE_TASK)
