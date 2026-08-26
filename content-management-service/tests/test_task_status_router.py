from collections.abc import Iterator
from typing import Final
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.celery_app import celery_app
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
)
from tests.support import authorization, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    NOTE_TASK_STATUS,
    OK,
    STATUS_PATHS,
    answered,
    owned_token,
)

_SUCCEEDED: Final[str] = "SUCCESS"
_PENDING: Final[str] = "PENDING"
_FAILED: Final[str] = "FAILURE"


class FakeAsyncResult:
    def __init__(self, status: str, result: object | None) -> None:
        self.status: str = status
        self.result: object | None = result

    def ready(self) -> bool:
        return self.result is not None


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


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
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        return_value=FakeAsyncResult(_SUCCEEDED, stored),
    ) as looked_up:
        _code, body = answered(
            client,
            path,
            owned_token(owned.folder_id),
            authorization(),
        )

    assert body[expected_key] == stored[expected_key]
    assert body["status"] == _SUCCEEDED
    assert looked_up.call_args.args[0] == CELERY_TASK_ID
    assert looked_up.call_args.kwargs["app"] is celery_app


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_pending_task_reports_only_its_status(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        return_value=FakeAsyncResult(_PENDING, None),
    ):
        _code, body = answered(
            client,
            path,
            owned_token(owned.folder_id),
            authorization(),
        )

    assert body == {"status": _PENDING}


def test_an_unfinished_result_object_is_rejected(
    client: TestClient, owned: OwnedContent
) -> None:
    with (
        mock.patch.object(
            task_status_router,
            "AsyncResult",
            return_value=FakeAsyncResult(
                _SUCCEEDED, ["not", "a", "dict"]
            ),
        ),
        pytest.raises(TypeError, match="did not finish with a result"),
    ):
        _ = answered(
            client,
            NOTE_TASK_STATUS,
            owned_token(owned.folder_id),
            authorization(),
        )


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_failed_task_reports_its_failure(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        return_value=FakeAsyncResult(
            _FAILED, RuntimeError("no folder")
        ),
    ):
        response = client.get(
            f"{path}/{owned_token(owned.folder_id)}",
            headers=authorization(),
        )

    assert response.status_code == OK
    assert response.json() == {"status": _FAILED}
