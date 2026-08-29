from collections.abc import Iterator
from contextlib import AbstractContextManager
from typing import Final
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.celery_app import celery_app
from features.study_units_generation.task_status_router import (
    _finished_result,
)
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
)
from tests.property_fakes import FakeAsyncResult
from tests.support import authorization, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    OK,
    STATUS_PATHS,
    answered,
    owned_token,
)

_SUCCEEDED: Final[str] = "SUCCESS"
_PENDING: Final[str] = "PENDING"
_FAILED: Final[str] = "FAILURE"
_FAILURE_BODY: Final[dict[str, object]] = {"status": _FAILED}
_TASK_ID: Final[str] = "abcdef01"
_NON_DICT_RESULTS: Final[tuple[object, ...]] = (
    None,
    ["not", "a", "dict"],
)


def _looking_up(
    status: str, result: object, *, ready: bool
) -> AbstractContextManager[object]:
    return mock.patch.object(
        task_status_router,
        "AsyncResult",
        FakeAsyncResult(status, result, finished=ready),
    )


def _recording_lookup(
    status: str, result: object, *, ready: bool
) -> AbstractContextManager[mock.MagicMock]:
    return mock.patch.object(
        task_status_router,
        "AsyncResult",
        wraps=FakeAsyncResult(status, result, finished=ready),
    )


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


def test_the_router_names_the_failure_status_it_substitutes() -> None:
    assert task_status_router._FAILED == _FAILED


def test_the_router_carries_no_unexpected_result_message() -> None:
    assert not hasattr(task_status_router, "_UNEXPECTED_RESULT")


@pytest.mark.parametrize("finished", _NON_DICT_RESULTS)
def test_a_succeeded_task_without_a_mapping_reports_a_failure(
    finished: object,
) -> None:
    with _looking_up(_SUCCEEDED, finished, ready=True):
        assert _finished_result(_TASK_ID) == (_FAILED, None)


@pytest.mark.parametrize(
    ("path", "stored", "expected_key"),
    [
        (
            "/flashcards-status",
            {"flashcard_deck_id": "d1"},
            "flashcard_deck_id",
        ),
        ("/test-task-status", {"test_id": "t1"}, "test_id"),
        ("/note-task-status", {"note_id": "n1"}, "note_id"),
    ],
)
def test_a_finished_task_reports_its_study_unit(
    client: TestClient,
    owned: OwnedContent,
    path: str,
    stored: dict[str, object],
    expected_key: str,
) -> None:
    with _recording_lookup(_SUCCEEDED, stored, ready=True) as looked_up:
        _code, body = answered(
            client, path, owned_token(owned.folder_id), authorization()
        )

    assert body[expected_key] == stored[expected_key]
    assert body["status"] == _SUCCEEDED
    assert looked_up.call_args.args[0] == CELERY_TASK_ID
    assert looked_up.call_args.kwargs["app"] is celery_app


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_pending_task_reports_only_its_status(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    with _looking_up(_PENDING, None, ready=False):
        _code, body = answered(
            client, path, owned_token(owned.folder_id), authorization()
        )

    assert body == {"status": _PENDING}


@pytest.mark.parametrize("path", STATUS_PATHS)
@pytest.mark.parametrize("finished", _NON_DICT_RESULTS)
def test_a_route_answers_a_bare_failure_for_a_non_dict_result(
    client: TestClient, owned: OwnedContent, path: str, finished: object
) -> None:
    with _looking_up(_SUCCEEDED, finished, ready=True):
        code, body = answered(
            client, path, owned_token(owned.folder_id), authorization()
        )

    assert code == OK
    assert body == _FAILURE_BODY


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_failed_task_reports_its_failure(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    with _looking_up(_FAILED, RuntimeError("no folder"), ready=True):
        code, body = answered(
            client, path, owned_token(owned.folder_id), authorization()
        )

    assert code == OK
    assert body == _FAILURE_BODY
