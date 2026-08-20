import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    HOME_ID,
    MISSING_TEST,
    OTHER_HOME_ID,
    OwnedContent,
    opened_test_sessions,
    scoped_client,
    seeded_content,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions

_NOT_FOUND = 404
_OK = 200
_UNAUTHORIZED = 401
_DEFAULT_PER_PAGE = 10


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


def _read_test_items(
    client: TestClient, test_id: str, headers: dict[str, str]
) -> tuple[int, dict[str, object]]:
    response = client.get(
        "/test-items", params={"test_id": test_id}, headers=headers
    )

    return response.status_code, cast("dict[str, object]", response.json())


def test_another_users_test_items_cannot_be_read(
    client: TestClient, owned: OwnedContent, intruder: dict[str, str]
) -> None:
    code, body = _read_test_items(client, owned.test_id, intruder)

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_TEST


def test_another_users_test_opens_no_session(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    _ = _read_test_items(client, owned.test_id, intruder)

    assert opened_test_sessions(sessions) == 0


def test_a_test_that_was_never_created_opens_no_session(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    assert owned.test_id

    code, body = _read_test_items(client, str(uuid.uuid4()), authorization())

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_TEST
    assert opened_test_sessions(sessions) == 0


def test_reading_test_items_without_a_token_is_refused(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = _read_test_items(client, owned.test_id, {})

    assert code == _UNAUTHORIZED
    assert "test_items" not in body
    assert opened_test_sessions(sessions) == 0


def test_an_owner_still_reads_their_own_test_items(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = _read_test_items(client, owned.test_id, authorization())
    items = cast("list[dict[str, object]]", body["test_items"])

    assert code == _OK
    assert body["total_items"] == 1
    assert body["page"] == 1
    assert body["per_page"] == _DEFAULT_PER_PAGE
    assert items[0]["type"] == "mult_choice"


def test_an_owners_reading_opens_one_session(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    _, body = _read_test_items(client, owned.test_id, authorization())

    assert body["test_session"]
    assert opened_test_sessions(sessions) == 1


def test_folder_scoped_items_are_still_listed(
    client: TestClient, owned: OwnedContent
) -> None:
    assert owned.test_id
    response = client.get(
        "/test-items", params={"folder_id": "home"}, headers=authorization()
    )
    body = cast("dict[str, object]", response.json())

    assert response.status_code == _OK
    assert body["total_items"] == 1
