import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units.assessment_router import TestItemsQuery
from tests.access_support import scoped_client
from tests.session_ownership_support import (
    OK,
    OwnedQuiz,
    seeded_quiz,
)
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import USER_ID, authorization, in_memory_sessions

_CALLER = uuid.UUID(USER_ID)
_RESPONSE_KEYS = {
    "test_items",
    "total_items",
    "test_session",
    "page",
    "per_page",
}
_ITEM_KEYS = {"id", "type", "content", "created_at", "last_answers"}


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


def _read(
    client: TestClient, parameters: dict[str, str]
) -> tuple[int, dict[str, object]]:
    response = client.get(
        "/test-items", params=parameters, headers=authorization()
    )

    return response.status_code, cast(
        "dict[str, object]", response.json()
    )


def test_query_still_exposes_test_session() -> None:
    assert "test_session" in TestItemsQuery.model_fields


def test_a_supplied_owned_session_is_echoed_back(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        supplied = opened_test_session(session, _CALLER, owned.test_id)

    code, body = _read(
        client,
        {"test_id": str(owned.test_id), "test_session": str(supplied)},
    )

    assert code == OK
    assert body["test_session"] == str(supplied)


def test_two_owner_reads_return_the_same_session_id(
    client: TestClient, owned: OwnedQuiz
) -> None:
    _, first = _read(client, {"test_id": str(owned.test_id)})
    _, second = _read(client, {"test_id": str(owned.test_id)})

    assert first["test_session"]
    assert first["test_session"] == second["test_session"]


def test_response_keys_are_unchanged(
    client: TestClient, owned: OwnedQuiz
) -> None:
    code, body = _read(client, {"test_id": str(owned.test_id)})
    items = cast("list[dict[str, object]]", body["test_items"])

    assert code == OK
    assert set(body) == _RESPONSE_KEYS
    assert set(items[0]) == _ITEM_KEYS


def test_an_empty_test_session_opens_a_fresh_one(
    client: TestClient, owned: OwnedQuiz
) -> None:
    code, body = _read(
        client, {"test_id": str(owned.test_id), "test_session": ""}
    )

    assert code == OK
    assert body["test_session"]
