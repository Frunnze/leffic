from typing import Literal

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.study_units_generation.generation_tasks import (
    generate_flashcards_task,
    generate_note_task,
    generate_test_task,
)
from features.study_units_generation.text_sources import (
    FileMetadata,
    text_from_files,
    text_from_link,
)
from shared.dependencies import AuthenticatedUserId

study_units_router = APIRouter()

_HOME_FOLDER = "home"
_NO_TEXT = "Could not extract text!"
_DEFAULT_TEST_AMOUNT = 10


class FlashcardsMetadata(BaseModel):
    comprehensiveness: Literal["high", "medium", "low"] | None = "medium"
    verbosity: Literal["high", "medium", "low"] | None = "low"
    types: list[Literal["basic", "list", "cloze"]] | None = None
    amount: int | None = None


class NoteMetadata(BaseModel):
    pass


class TestMetadata(BaseModel):
    amount: int = _DEFAULT_TEST_AMOUNT


class StudyUnitsMetadata(BaseModel):
    folder_id: str | None = None
    file_metadata: list[FileMetadata] | None = None
    link_metadata: str | None = None
    topic_metadata: str | None = None
    flashcards: FlashcardsMetadata | None = None
    note: NoteMetadata | None = None
    test: TestMetadata | None = None
    ai_model: str | None = None


def _extracted_text(request_data: StudyUnitsMetadata) -> str:
    if request_data.file_metadata:
        return text_from_files(request_data.file_metadata)

    if request_data.link_metadata:
        return text_from_link(request_data.link_metadata)

    if request_data.topic_metadata:
        return f"Topic/Text: {request_data.topic_metadata}"

    return ""


def _queued_tasks(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    if request_data.flashcards:
        queued["task_id"] = generate_flashcards_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            flashcards_metadata=request_data.flashcards.model_dump(),
            folder_id=folder_id,
            user_id=user_id,
        ).id

    if request_data.test:
        queued["test_task_id"] = generate_test_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


@study_units_router.post("/generate-study-units", response_model=None)
async def generate_study_units(
    request_data: StudyUnitsMetadata, user_id: AuthenticatedUserId
) -> dict[str, object] | JSONResponse:
    folder_id = (
        user_id
        if request_data.folder_id == _HOME_FOLDER
        else request_data.folder_id
    )
    extracted_text = _extracted_text(request_data)

    if not extracted_text or folder_id is None:
        return JSONResponse(
            content={"msg": _NO_TEXT},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if request_data.link_metadata:
        extracted_text += (
            "The source link to mention in notes: "
            f"{request_data.link_metadata}"
        )

    return _queued_tasks(request_data, extracted_text, folder_id, user_id)
