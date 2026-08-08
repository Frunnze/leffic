from datetime import UTC, datetime
from typing import cast

from celery.result import AsyncResult
from fastapi import APIRouter

from shared.celery_app import celery_app

task_status_router = APIRouter()


def _finished_result(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    return status, cast("dict[str, object]", task_result.result)


@task_status_router.get("/flashcards-status/{task_id}")
def get_flashcard_status(task_id: str) -> dict[str, object]:
    status, result = _finished_result(task_id)

    if result is None:
        return {"status": status}

    return {
        "status": status,
        "flashcard_deck_id": result.get("flashcard_deck_id"),
        "type": "flashcard_deck",
        "name": result.get("deck_name"),
        "created_at": datetime.now(UTC).isoformat(),
    }


@task_status_router.get("/test-task-status/{task_id}")
def get_test_task_status(task_id: str) -> dict[str, object]:
    status, result = _finished_result(task_id)

    if result is None:
        return {"status": status}

    return {
        "status": status,
        "test_id": result.get("test_id"),
        "type": "test",
        "name": result.get("test_name"),
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
