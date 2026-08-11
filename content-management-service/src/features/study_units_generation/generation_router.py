from typing import Literal

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.study_units_generation.generation_tasks import (
    generate_flashcards_task,
    generate_note_task,
    generate_test_task,
)
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import ensured_home_folder

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


class GenerationRequest(BaseModel):
    text: str
    folder_id: str | None = None
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

    return _queued_tasks(request_data, folder_id)


def _queued_tasks(
    request_data: GenerationRequest, folder_id: str
) -> dict[str, object]:
    queued: dict[str, object] = {}
    shared_arguments: dict[str, object] = {
        "ai_model": request_data.ai_model,
        "extracted_text": request_data.text,
        "folder_id": folder_id,
    }

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
            **shared_arguments
        ).id

    if request_data.flashcards:
        queued["task_id"] = generate_flashcards_task.delay(
            **shared_arguments,
            flashcards_metadata=request_data.flashcards.model_dump(),
        ).id

    if request_data.test:
        queued["test_task_id"] = generate_test_task.delay(
            **shared_arguments
        ).id

    return queued
