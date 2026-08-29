import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import Folder, TestSession
from tests.access_support import scoped_client
from tests.session_ownership_support import (
    MISSING_FOLDER_DETAIL,
    NOT_FOUND,
    OK,
    OwnedQuiz,
    seeded_quiz,
)
from tests.support import USER_ID, authorization, in_memory_sessions

_CALLER = uuid.UUID(USER_ID)
_MALFORMED = "not-a-uuid"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def stranger_quiz(sessions: sessionmaker[Session]) -> OwnedQuiz:
    with sessions() as session:
        return seeded_quiz(session, uuid.uuid4())


def _read(
    client: TestClient, parameters: dict[str, str]
) -> tuple[int, dict[str, object]]:
    response = client.get(
        "/test-items",
        params=parameters,
        headers=authorization(),
    )

    return response.status_code, cast(
        "dict[str, object]", response.json()
    )


def _open_sessions(sessions: sessionmaker[Session]) -> int:
    with sessions() as session:
        return session.query(TestSession).count()


def test_a_foreign_folder_is_refused(
    client: TestClient, stranger_quiz: OwnedQuiz
) -> None:
    code, body = _read(
        client, {"folder_id": str(stranger_quiz.folder_id)}
    )

    assert code == NOT_FOUND
    assert body["detail"] == MISSING_FOLDER_DETAIL


def test_home_without_a_folder_row_is_now_404(
    client: TestClient,
) -> None:
    code, body = _read(client, {"folder_id": "home"})

    assert code == NOT_FOUND
    assert body["detail"] == MISSING_FOLDER_DETAIL


def test_a_refused_read_opens_no_session(
    client: TestClient,
    sessions: sessionmaker[Session],
    stranger_quiz: OwnedQuiz,
) -> None:
    _ = _read(client, {"test_id": str(stranger_quiz.test_id)})
    _ = _read(client, {"folder_id": str(stranger_quiz.folder_id)})
    _ = _read(client, {"folder_id": _MALFORMED})
    _ = _read(client, {"test_id": _MALFORMED})
    _ = _read(client, {"folder_id": "home"})

    assert _open_sessions(sessions) == 0


def test_an_owned_folder_is_still_listed(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        owned = seeded_quiz(session, _CALLER)

    code, body = _read(client, {"folder_id": str(owned.folder_id)})

    assert code == OK
    assert body["total_items"] == 1


def test_a_home_folder_owned_by_someone_else_is_refused(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = seeded_quiz(session, _CALLER)
        home = session.query(Folder).filter_by(id=_CALLER).one()
        home.user_id = uuid.uuid4()
        session.commit()

    code, body = _read(client, {"folder_id": "home"})

    assert code == NOT_FOUND
    assert body["detail"] == MISSING_FOLDER_DETAIL


def test_an_empty_folder_id_is_refused_like_a_malformed_one(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    empty = _read(client, {"folder_id": ""})
    malformed = _read(client, {"folder_id": _MALFORMED})

    assert empty == malformed
    assert empty[0] == NOT_FOUND
    assert empty[1]["detail"] == MISSING_FOLDER_DETAIL
    assert _open_sessions(sessions) == 0
