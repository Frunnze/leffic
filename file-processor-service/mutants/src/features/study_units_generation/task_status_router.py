from datetime import UTC, datetime
from typing import TypeGuard

from celery.result import AsyncResult
from fastapi import APIRouter

from shared.celery_app import celery_app

task_status_router = APIRouter()

_UNEXPECTED_RESULT = "The task did not finish with a result object"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


def _is_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)
mutants_x__finished_result__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__finished_result__mutmut)
def _finished_result(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_orig(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_1(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = None
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_2(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(None, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_3(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=None)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_4(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_5(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, )
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_6(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = None

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_7(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_8(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = None

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_9(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(None):
        return status, finished

    raise TypeError(_UNEXPECTED_RESULT)


def x__finished_result__mutmut_10(task_id: str) -> tuple[str, dict[str, object] | None]:
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status

    if not task_result.ready():
        return status, None

    finished: object = task_result.result

    if _is_object_dict(finished):
        return status, finished

    raise TypeError(None)

mutants_x__finished_result__mutmut['_mutmut_orig'] = x__finished_result__mutmut_orig # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_1'] = x__finished_result__mutmut_1 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_2'] = x__finished_result__mutmut_2 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_3'] = x__finished_result__mutmut_3 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_4'] = x__finished_result__mutmut_4 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_5'] = x__finished_result__mutmut_5 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_6'] = x__finished_result__mutmut_6 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_7'] = x__finished_result__mutmut_7 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_8'] = x__finished_result__mutmut_8 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_9'] = x__finished_result__mutmut_9 # type: ignore # mutmut generated
mutants_x__finished_result__mutmut['x__finished_result__mutmut_10'] = x__finished_result__mutmut_10 # type: ignore # mutmut generated


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
