import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    HOME_ID,
    MISSING_NOTE,
    OTHER_HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions

_NOT_FOUND = 404
_OK = 200
_UNAUTHORIZED = 401


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def intruder(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


def _read_note(
    client: TestClient, note_id: str, headers: dict[str, str]
) -> tuple[int, dict[str, object]]:
    response = client.get(
        "/note", params={"note_id": note_id}, headers=headers
    )

    return response.status_code, cast("dict[str, object]", response.json())


def test_another_users_note_cannot_be_read(
    client: TestClient, owned: OwnedContent, intruder: dict[str, str]
) -> None:
    code, body = _read_note(client, owned.note_id, intruder)

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_NOTE


def test_reading_a_note_without_a_token_is_refused(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = _read_note(client, owned.note_id, {})

    assert code == _UNAUTHORIZED
    assert "content" not in body


def test_an_owner_still_reads_their_own_note(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = _read_note(client, owned.note_id, authorization())

    assert code == _OK
    assert body == {"content": "body", "name": "N", "read": False}


def test_a_note_that_was_never_created_is_reported_as_missing(
    client: TestClient, owned: OwnedContent
) -> None:
    assert owned.note_id

    code, body = _read_note(client, str(uuid.uuid4()), authorization())

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_NOTE
