import uuid
from datetime import UTC, datetime
from typing import TypeGuard

from celery.result import AsyncResult
from fastapi import APIRouter

from features.study_units_generation.celery_app import celery_app
from shared.dependencies import DatabaseSession
from shared.models import FlashcardDeck, Test

task_status_router = APIRouter()

_UNEXPECTED_RESULT = "The task did not finish with a result object"
_SUCCEEDED = "SUCCESS"


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

    raise TypeError(_UNEXPECTED_RESULT)


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


@task_status_router.get("/flashcards-status/{task_id}")
def get_flashcard_status(
    task_id: str, db: DatabaseSession
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


@task_status_router.get("/test-task-status/{task_id}")
def get_test_task_status(
    task_id: str, db: DatabaseSession
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


@task_status_router.get("/note-task-status/{task_id}")
def get_note_task_status(task_id: str) -> dict[str, object]:
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
