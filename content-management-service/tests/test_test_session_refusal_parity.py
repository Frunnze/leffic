import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import scoped_client
from tests.session_ownership_support import (
    MISSING_SESSION_DETAIL,
    NOT_FOUND,
    OwnedQuiz,
    seeded_quiz,
)
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import USER_ID, authorization, in_memory_sessions

_CALLER = uuid.UUID(USER_ID)
_UNPARSEABLE = "not-a-uuid"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedQuiz:
    with sessions() as session:
        return seeded_quiz(session, _CALLER)


def _supplied_session_ids(
    sessions: sessionmaker[Session], owned: OwnedQuiz
) -> tuple[str, ...]:
    with sessions() as session:
        foreign = opened_test_session(
            session, uuid.uuid4(), owned.test_id
        )
        elsewhere = opened_test_session(session, _CALLER, uuid.uuid4())

    return (
        _UNPARSEABLE,
        str(uuid.uuid4()),
        str(foreign),
        str(elsewhere),
    )


def _refusal(
    client: TestClient, owned: OwnedQuiz, supplied: str
) -> tuple[int, str]:
    response = client.get(
        "/test-items",
        params={
            "test_id": str(owned.test_id),
            "test_session": supplied,
        },
        headers=authorization(),
    )
    body = cast("dict[str, str]", response.json())

    return response.status_code, body.get("detail", "")


def test_every_supplied_session_refusal_is_the_same_404(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    refusals = {
        _refusal(client, owned, supplied)
        for supplied in _supplied_session_ids(sessions, owned)
    }

    assert refusals == {(NOT_FOUND, MISSING_SESSION_DETAIL)}
