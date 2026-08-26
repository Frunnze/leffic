from collections.abc import Iterator
from typing import Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import MISSING_TASK
from features.study_units_generation.task_status_router import (
    _owned_task_id,
)
from tests.access_support import (
    HOME_ID,
    MISSING_FOLDER,
    OTHER_HOME_ID,
    OwnedContent,
    crashless_client,
    seeded_content,
)
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    authorization,
    in_memory_sessions,
)
from tests.task_token_support import (
    CELERY_TASK_ID,
    FLASHCARDS_STATUS,
    NOT_FOUND,
    NOTE_TASK_STATUS,
    STATUS_PATHS,
    TEST_TASK_STATUS,
    UNAUTHORIZED,
    RefusingAsyncResult,
    answered,
    forged_token,
    owned_token,
)

_REFUSAL_BODY: Final[dict[str, str]] = {"detail": MISSING_TASK}


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def intruder(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


@pytest.fixture
def refusing_celery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        task_status_router, "AsyncResult", RefusingAsyncResult()
    )


def test_helper_returns_the_bare_task_id_for_the_owner(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    with sessions() as session:
        resolved = _owned_task_id(
            task_id=owned_token(owned.folder_id),
            user_id=USER_ID,
            db=session,
        )

    assert resolved == CELERY_TASK_ID


@pytest.mark.usefixtures("refusing_celery")
def test_foreign_folder_reuses_the_task_detail(
    client: TestClient,
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = answered(
        client, NOTE_TASK_STATUS, owned_token(owned.folder_id), intruder
    )

    assert code == NOT_FOUND
    assert body == _REFUSAL_BODY
    assert body["detail"] != MISSING_FOLDER


@pytest.mark.usefixtures("refusing_celery")
def test_flashcards_status_rejects_a_foreign_folder(
    client: TestClient,
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = answered(
        client, FLASHCARDS_STATUS, owned_token(owned.folder_id), intruder
    )

    assert (code, body) == (NOT_FOUND, _REFUSAL_BODY)


@pytest.mark.usefixtures("refusing_celery")
def test_test_task_status_rejects_a_foreign_folder(
    client: TestClient,
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = answered(
        client, TEST_TASK_STATUS, owned_token(owned.folder_id), intruder
    )

    assert (code, body) == (NOT_FOUND, _REFUSAL_BODY)


@pytest.mark.usefixtures("refusing_celery")
def test_note_task_status_rejects_a_foreign_folder(
    client: TestClient,
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = answered(
        client, NOTE_TASK_STATUS, owned_token(owned.folder_id), intruder
    )

    assert (code, body) == (NOT_FOUND, _REFUSAL_BODY)


@pytest.mark.usefixtures("refusing_celery")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_rejected_token_never_touches_celery_or_the_database(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    code, body = answered(
        client, path, forged_token(owned.folder_id), authorization()
    )

    assert (code, body) == (NOT_FOUND, _REFUSAL_BODY)


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_missing_token_is_unauthorized(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    code, _body = answered(
        client, path, owned_token(owned.folder_id), {}
    )

    assert code == UNAUTHORIZED
