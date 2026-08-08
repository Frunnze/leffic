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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


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
mutants_x__extracted_text__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__extracted_text__mutmut)
def _extracted_text(request_data: StudyUnitsMetadata) -> str:
    if request_data.file_metadata:
        return text_from_files(request_data.file_metadata)

    if request_data.link_metadata:
        return text_from_link(request_data.link_metadata)

    if request_data.topic_metadata:
        return f"Topic/Text: {request_data.topic_metadata}"

    return ""


def x__extracted_text__mutmut_orig(request_data: StudyUnitsMetadata) -> str:
    if request_data.file_metadata:
        return text_from_files(request_data.file_metadata)

    if request_data.link_metadata:
        return text_from_link(request_data.link_metadata)

    if request_data.topic_metadata:
        return f"Topic/Text: {request_data.topic_metadata}"

    return ""


def x__extracted_text__mutmut_1(request_data: StudyUnitsMetadata) -> str:
    if request_data.file_metadata:
        return text_from_files(None)

    if request_data.link_metadata:
        return text_from_link(request_data.link_metadata)

    if request_data.topic_metadata:
        return f"Topic/Text: {request_data.topic_metadata}"

    return ""


def x__extracted_text__mutmut_2(request_data: StudyUnitsMetadata) -> str:
    if request_data.file_metadata:
        return text_from_files(request_data.file_metadata)

    if request_data.link_metadata:
        return text_from_link(None)

    if request_data.topic_metadata:
        return f"Topic/Text: {request_data.topic_metadata}"

    return ""


def x__extracted_text__mutmut_3(request_data: StudyUnitsMetadata) -> str:
    if request_data.file_metadata:
        return text_from_files(request_data.file_metadata)

    if request_data.link_metadata:
        return text_from_link(request_data.link_metadata)

    if request_data.topic_metadata:
        return f"Topic/Text: {request_data.topic_metadata}"

    return "XXXX"

mutants_x__extracted_text__mutmut['_mutmut_orig'] = x__extracted_text__mutmut_orig # type: ignore # mutmut generated
mutants_x__extracted_text__mutmut['x__extracted_text__mutmut_1'] = x__extracted_text__mutmut_1 # type: ignore # mutmut generated
mutants_x__extracted_text__mutmut['x__extracted_text__mutmut_2'] = x__extracted_text__mutmut_2 # type: ignore # mutmut generated
mutants_x__extracted_text__mutmut['x__extracted_text__mutmut_3'] = x__extracted_text__mutmut_3 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__queued_tasks__mutmut)
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


def x__queued_tasks__mutmut_orig(
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


def x__queued_tasks__mutmut_1(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = None

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


def x__queued_tasks__mutmut_2(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["note_task_id"] = None

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


def x__queued_tasks__mutmut_3(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["XXnote_task_idXX"] = generate_note_task.delay(
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


def x__queued_tasks__mutmut_4(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["NOTE_TASK_ID"] = generate_note_task.delay(
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


def x__queued_tasks__mutmut_5(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
            ai_model=None,
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


def x__queued_tasks__mutmut_6(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=None,
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


def x__queued_tasks__mutmut_7(
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
            folder_id=None,
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


def x__queued_tasks__mutmut_8(
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
            user_id=None,
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


def x__queued_tasks__mutmut_9(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
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


def x__queued_tasks__mutmut_10(
    request_data: StudyUnitsMetadata,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    queued: dict[str, object] = {}

    if request_data.note:
        queued["note_task_id"] = generate_note_task.delay(
            ai_model=request_data.ai_model,
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


def x__queued_tasks__mutmut_11(
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


def x__queued_tasks__mutmut_12(
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


def x__queued_tasks__mutmut_13(
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
        queued["task_id"] = None

    if request_data.test:
        queued["test_task_id"] = generate_test_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_14(
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
        queued["XXtask_idXX"] = generate_flashcards_task.delay(
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


def x__queued_tasks__mutmut_15(
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
        queued["TASK_ID"] = generate_flashcards_task.delay(
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


def x__queued_tasks__mutmut_16(
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
            ai_model=None,
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


def x__queued_tasks__mutmut_17(
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
            extracted_text=None,
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


def x__queued_tasks__mutmut_18(
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
            flashcards_metadata=None,
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


def x__queued_tasks__mutmut_19(
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
            folder_id=None,
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


def x__queued_tasks__mutmut_20(
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
            user_id=None,
        ).id

    if request_data.test:
        queued["test_task_id"] = generate_test_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_21(
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


def x__queued_tasks__mutmut_22(
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


def x__queued_tasks__mutmut_23(
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


def x__queued_tasks__mutmut_24(
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


def x__queued_tasks__mutmut_25(
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
            ).id

    if request_data.test:
        queued["test_task_id"] = generate_test_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_26(
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
        queued["test_task_id"] = None

    return queued


def x__queued_tasks__mutmut_27(
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
        queued["XXtest_task_idXX"] = generate_test_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_28(
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
        queued["TEST_TASK_ID"] = generate_test_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_29(
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
            ai_model=None,
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_30(
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
            extracted_text=None,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_31(
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
            folder_id=None,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_32(
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
            user_id=None,
        ).id

    return queued


def x__queued_tasks__mutmut_33(
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
            extracted_text=extracted_text,
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_34(
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
            folder_id=folder_id,
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_35(
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
            user_id=user_id,
        ).id

    return queued


def x__queued_tasks__mutmut_36(
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
            ).id

    return queued

mutants_x__queued_tasks__mutmut['_mutmut_orig'] = x__queued_tasks__mutmut_orig # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_1'] = x__queued_tasks__mutmut_1 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_2'] = x__queued_tasks__mutmut_2 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_3'] = x__queued_tasks__mutmut_3 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_4'] = x__queued_tasks__mutmut_4 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_5'] = x__queued_tasks__mutmut_5 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_6'] = x__queued_tasks__mutmut_6 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_7'] = x__queued_tasks__mutmut_7 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_8'] = x__queued_tasks__mutmut_8 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_9'] = x__queued_tasks__mutmut_9 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_10'] = x__queued_tasks__mutmut_10 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_11'] = x__queued_tasks__mutmut_11 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_12'] = x__queued_tasks__mutmut_12 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_13'] = x__queued_tasks__mutmut_13 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_14'] = x__queued_tasks__mutmut_14 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_15'] = x__queued_tasks__mutmut_15 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_16'] = x__queued_tasks__mutmut_16 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_17'] = x__queued_tasks__mutmut_17 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_18'] = x__queued_tasks__mutmut_18 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_19'] = x__queued_tasks__mutmut_19 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_20'] = x__queued_tasks__mutmut_20 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_21'] = x__queued_tasks__mutmut_21 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_22'] = x__queued_tasks__mutmut_22 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_23'] = x__queued_tasks__mutmut_23 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_24'] = x__queued_tasks__mutmut_24 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_25'] = x__queued_tasks__mutmut_25 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_26'] = x__queued_tasks__mutmut_26 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_27'] = x__queued_tasks__mutmut_27 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_28'] = x__queued_tasks__mutmut_28 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_29'] = x__queued_tasks__mutmut_29 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_30'] = x__queued_tasks__mutmut_30 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_31'] = x__queued_tasks__mutmut_31 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_32'] = x__queued_tasks__mutmut_32 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_33'] = x__queued_tasks__mutmut_33 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_34'] = x__queued_tasks__mutmut_34 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_35'] = x__queued_tasks__mutmut_35 # type: ignore # mutmut generated
mutants_x__queued_tasks__mutmut['x__queued_tasks__mutmut_36'] = x__queued_tasks__mutmut_36 # type: ignore # mutmut generated


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
