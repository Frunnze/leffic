import uuid
from datetime import UTC, datetime
from typing import Annotated, Final, TypeGuard

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, params

from features.study_units_generation.celery_app import celery_app
from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    verified_task_id,
)
from shared.claims_extractor import get_user_id_from_jwt
from shared.database import get_db
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import owned_folder
from shared.models import FlashcardDeck, Test

task_status_router = APIRouter()

_SCOPED_TO_THE_CALLER: Final[list[params.Depends]] = [
    Depends(get_user_id_from_jwt),
    Depends(get_db),
]
_SUCCEEDED: Final[str] = "SUCCESS"
_FAILED: Final[str] = "FAILURE"


def _is_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def _finished_result(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready() or status != _SUCCEEDED:
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    return _FAILED, None


def _as_identifier(row_id: object) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(row_id))
    except ValueError:
        return None


def _deck_name(db: DatabaseSession, deck_id: object) -> str | None:
    identifier = _as_identifier(deck_id)

    if identifier is None:
        return None

    deck = db.query(FlashcardDeck).filter_by(id=identifier).first()

    return None if deck is None else str(deck.name)


def _test_name(db: DatabaseSession, test_id: object) -> str | None:
    identifier = _as_identifier(test_id)

    if identifier is None:
        return None

    test = db.query(Test).filter_by(id=identifier).first()

    return None if test is None else str(test.name)


def _owned_task_id(
    task_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> str:
    celery_task_id, folder_id = verified_task_id(task_id)
    _ = owned_folder(db, user_id, folder_id, MISSING_TASK)

    return celery_task_id


OwnedTaskId = Annotated[str, Depends(_owned_task_id)]


@task_status_router.get(
    "/flashcards-status/{task_id}", dependencies=_SCOPED_TO_THE_CALLER
)
def get_flashcard_status(
    task_id: OwnedTaskId, db: DatabaseSession
) -> dict[str, object]:
    status, result = _finished_result(task_id)

    if result is None:
        return {"status": status}

    deck_id = result.get("flashcard_deck_id")

    return {
        "status": status,
        "flashcard_deck_id": deck_id,
        "type": "flashcard_deck",
        "flashcard_type": result.get("type"),
        "written": result.get("written"),
        "name": _deck_name(db, deck_id),
        "created_at": datetime.now(UTC).isoformat(),
    }


@task_status_router.get(
    "/test-task-status/{task_id}", dependencies=_SCOPED_TO_THE_CALLER
)
def get_test_task_status(
    task_id: OwnedTaskId, db: DatabaseSession
) -> dict[str, object]:
    status, result = _finished_result(task_id)

    if result is None:
        return {"status": status}

    test_id = result.get("test_id")

    return {
        "status": status,
        "test_id": test_id,
        "type": "test",
        "test_item_type": result.get("type"),
        "written": result.get("written"),
        "name": _test_name(db, test_id),
        "created_at": datetime.now(UTC).isoformat(),
    }


@task_status_router.get(
    "/note-task-status/{task_id}", dependencies=_SCOPED_TO_THE_CALLER
)
def get_note_task_status(
    task_id: OwnedTaskId,
) -> dict[str, object]:
    status, result = _finished_result(task_id)

    if result is None:
        return {"status": status}

    return {
        "status": status,
        "note_id": result.get("note_id"),
        "type": "note",
        "name": result.get("note_name"),
        "created_at": datetime.now(UTC).isoformat(),
    }
