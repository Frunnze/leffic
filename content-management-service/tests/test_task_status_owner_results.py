from collections.abc import Iterator
from typing import Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
)
from tests.support import authorization, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    FLASHCARDS_STATUS,
    NOTE_TASK_STATUS,
    OK,
    STATUS_PATHS,
    TEST_TASK_STATUS,
    PendingAsyncResult,
    SucceededAsyncResult,
    answered,
    owned_token,
)

_PENDING_BODY: Final[dict[str, str]] = {"status": "PENDING"}
_SUCCEEDED: Final[str] = "SUCCESS"
_WRITTEN_COUNT: Final[int] = 12
_DECK_KEYS: Final[frozenset[str]] = frozenset({
    "status",
    "flashcard_deck_id",
    "type",
    "flashcard_type",
    "written",
    "name",
    "created_at",
})
_TEST_KEYS: Final[frozenset[str]] = frozenset({
    "status",
    "test_id",
    "type",
    "test_item_type",
    "written",
    "name",
    "created_at",
})
_NOTE_KEYS: Final[frozenset[str]] = frozenset({
    "status",
    "note_id",
    "type",
    "name",
    "created_at",
})


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_owned_pending_task_still_answers_200_pending(
    client: TestClient,
    owned: OwnedContent,
    path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    celery = PendingAsyncResult()
    monkeypatch.setattr(task_status_router, "AsyncResult", celery)

    code, body = answered(
        client, path, owned_token(owned.folder_id), authorization()
    )

    assert (code, body) == (OK, _PENDING_BODY)
    assert celery.looked_up == [CELERY_TASK_ID]


def test_owned_successful_task_body_is_unchanged_for_flashcards(
    client: TestClient,
    owned: OwnedContent,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    finished: dict[str, object] = {
        "flashcard_deck_id": owned.deck_id,
        "type": "basic",
        "written": _WRITTEN_COUNT,
    }
    celery = SucceededAsyncResult(finished)
    monkeypatch.setattr(task_status_router, "AsyncResult", celery)

    code, body = answered(
        client,
        FLASHCARDS_STATUS,
        owned_token(owned.folder_id),
        authorization(),
    )

    assert code == OK
    assert frozenset(body) == _DECK_KEYS
    assert body["status"] == _SUCCEEDED
    assert body["flashcard_deck_id"] == owned.deck_id
    assert body["type"] == "flashcard_deck"
    assert body["flashcard_type"] == "basic"
    assert body["written"] == _WRITTEN_COUNT
    assert body["name"] == "Deck"
    assert celery.looked_up == [CELERY_TASK_ID]


def test_owned_successful_task_body_is_unchanged_for_tests(
    client: TestClient,
    owned: OwnedContent,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    finished: dict[str, object] = {
        "test_id": owned.test_id,
        "type": "short_answer",
        "written": _WRITTEN_COUNT,
    }
    celery = SucceededAsyncResult(finished)
    monkeypatch.setattr(task_status_router, "AsyncResult", celery)

    code, body = answered(
        client,
        TEST_TASK_STATUS,
        owned_token(owned.folder_id),
        authorization(),
    )

    assert code == OK
    assert frozenset(body) == _TEST_KEYS
    assert body["test_id"] == owned.test_id
    assert body["type"] == "test"
    assert body["test_item_type"] == "short_answer"
    assert body["written"] == _WRITTEN_COUNT
    assert body["name"] == "Quiz"
    assert celery.looked_up == [CELERY_TASK_ID]


def test_owned_successful_task_body_is_unchanged_for_notes(
    client: TestClient,
    owned: OwnedContent,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    finished: dict[str, object] = {
        "note_id": owned.note_id,
        "note_name": "Cell biology",
    }
    celery = SucceededAsyncResult(finished)
    monkeypatch.setattr(task_status_router, "AsyncResult", celery)

    code, body = answered(
        client,
        NOTE_TASK_STATUS,
        owned_token(owned.folder_id),
        authorization(),
    )

    assert code == OK
    assert frozenset(body) == _NOTE_KEYS
    assert body["note_id"] == owned.note_id
    assert body["type"] == "note"
    assert body["name"] == "Cell biology"
    assert celery.looked_up == [CELERY_TASK_ID]
