from typing import Literal

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.study_units_generation.assessment_writer import create_test
from features.study_units_generation.flashcard_deck_writer import (
    create_flashcard_deck,
)
from features.study_units_generation.generation_tasks import (
    generate_flashcards_of_type_task,
    generate_note_task,
    generate_test_items_of_type_task,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_types import (
    DEFAULT_FLASHCARD_TYPES,
    DEFAULT_TEST_ITEM_TYPES,
    requested_names,
)
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import ensured_home_folder, owned_folder_id

generation_router = APIRouter()

_HOME_FOLDER = "home"
_NO_TEXT = "There is no text to generate from!"
_DEFAULT_TEST_AMOUNT = 10


class FlashcardsMetadata(BaseModel):
    comprehensiveness: Literal["high", "medium", "low"] | None = "medium"
    verbosity: Literal["high", "medium", "low"] | None = "low"
    types: (
        list[Literal["basic", "list", "cloze", "feynman"]] | None
    ) = None
    amount: int | None = None


class NoteMetadata(BaseModel):
    pass


class TestMetadata(BaseModel):
    amount: int = _DEFAULT_TEST_AMOUNT
    types: (
        list[Literal["multiple_choice", "true_or_false", "short_answer"]]
        | None
    ) = None


class GenerationRequest(BaseModel):
    text: str
    folder_id: str | None = None
    source_kind: Literal["file", "link", "topic", "text"] | None = None
    source_reference: str | None = None
    flashcards: FlashcardsMetadata | None = None
    note: NoteMetadata | None = None
    test: TestMetadata | None = None
    ai_model: str | None = None


@generation_router.post("/generate-study-units", response_model=None)
async def generate_study_units(
    request_data: GenerationRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> dict[str, object] | JSONResponse:
    folder_id = request_data.folder_id

    if folder_id == _HOME_FOLDER:
        folder_id = str(ensured_home_folder(db, user_id).id)

    if not request_data.text.strip() or folder_id is None:
        return JSONResponse(
            content={"msg": _NO_TEXT},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return _queued_tasks(
        request_data, owned_folder_id(db, user_id, folder_id), db
    )


def _queued_tasks(
    request_data: GenerationRequest,
    folder_id: str,
    db: DatabaseSession,
) -> dict[str, object]:
    queued: dict[str, object] = {}
    source = StudyUnitSource(
        kind=request_data.source_kind,
        reference=request_data.source_reference,
    )

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=request_data.text,
            folder_id=folder_id,
            source_kind=request_data.source_kind,
            source_reference=request_data.source_reference,
        ).id

    if request_data.flashcards:
        queued.update(
            _queued_flashcards(request_data, folder_id, db, source)
        )

    if request_data.test:
        queued.update(_queued_test(request_data, folder_id, db, source))

    return queued


def _queued_flashcards(
    request_data: GenerationRequest,
    folder_id: str,
    db: DatabaseSession,
    source: StudyUnitSource,
) -> dict[str, object]:
    wanted = request_data.flashcards or FlashcardsMetadata()
    deck_id = create_flashcard_deck(db, folder_id, source)
    task_ids: list[str] = []

    for flashcard_type in requested_names(
        tuple(wanted.types or ()), DEFAULT_FLASHCARD_TYPES
    ):
        task_ids.append(
            generate_flashcards_of_type_task.delay(
                ai_model=request_data.ai_model,
                extracted_text=request_data.text,
                deck_id=deck_id,
                flashcard_type=flashcard_type,
                comprehensiveness=wanted.comprehensiveness or "medium",
                verbosity=wanted.verbosity or "low",
                amount=wanted.amount,
            ).id
        )

    return {"flashcard_deck_id": deck_id, "flashcard_task_ids": task_ids}


def _queued_test(
    request_data: GenerationRequest,
    folder_id: str,
    db: DatabaseSession,
    source: StudyUnitSource,
) -> dict[str, object]:
    wanted = request_data.test or TestMetadata()
    test_id = create_test(db, folder_id, source)
    task_ids: list[str] = []

    for item_type in requested_names(
        tuple(wanted.types or ()), DEFAULT_TEST_ITEM_TYPES
    ):
        task_ids.append(
            generate_test_items_of_type_task.delay(
                ai_model=request_data.ai_model,
                extracted_text=request_data.text,
                test_id=test_id,
                item_type=item_type,
                amount=wanted.amount,
            ).id
        )

    return {"test_id": test_id, "test_task_ids": task_ids}
