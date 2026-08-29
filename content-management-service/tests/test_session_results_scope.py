import inspect
import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import assessment_stats_router
from shared.folder_access import resolved_folder_id
from shared.models import TestSession
from tests.access_support import scoped_client
from tests.session_ownership_support import (
    DONE,
    NO_TEST_STATS_DETAIL,
    NOT_FOUND,
    ONGOING,
    UNAUTHORIZED,
    WRONG_ANSWER,
    OwnedQuiz,
    review_body,
    seeded_quiz,
)
from tests.study_unit_access_support import opened_test_session
from tests.support import USER_ID, authorization, in_memory_sessions

_CALLER = uuid.UUID(USER_ID)
_UNPARSEABLE = "not-a-uuid"
_STATS_PARAMETERS = ("folder_id", "db", "user_id")


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


def _results(
    client: TestClient, test_session: str, headers: dict[str, str]
) -> tuple[int, dict[str, str]]:
    response = client.get(
        "/test-session-results",
        params={"test_session": test_session},
        headers=headers,
    )

    return response.status_code, cast(
        "dict[str, str]", response.json()
    )


def _status_of(
    sessions: sessionmaker[Session], session_id: uuid.UUID
) -> str:
    with sessions() as session:
        row = session.get(TestSession, session_id)

        assert row is not None

        return row.status


def test_test_session_results_requires_a_caller(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        mine = opened_test_session(session, _CALLER, owned.test_id)

    code, _ = _results(client, str(mine), {})

    assert code == UNAUTHORIZED
    assert _status_of(sessions, mine) == ONGOING


def test_a_foreign_or_unknown_session_is_refused(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        theirs = opened_test_session(
            session, uuid.uuid4(), owned.test_id
        )

    supplied_ids = (str(uuid.uuid4()), _UNPARSEABLE, str(theirs))
    refusals: set[tuple[int, str]] = set()

    for supplied in supplied_ids:
        code, body = _results(client, supplied, authorization())
        refusals.add((code, body.get("detail", "")))

    assert refusals == {(NOT_FOUND, NO_TEST_STATS_DETAIL)}
    assert _status_of(sessions, theirs) == ONGOING


def test_a_zero_score_owned_session_is_closed_then_404(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        mine = opened_test_session(session, _CALLER, owned.test_id)

    _ = client.post(
        "/review-test-item",
        json=review_body(owned.test_item_id, mine, WRONG_ANSWER),
        headers=authorization(),
    )

    code, body = _results(client, str(mine), authorization())

    assert code == NOT_FOUND
    assert body == {"msg": NO_TEST_STATS_DETAIL}
    assert _status_of(sessions, mine) == DONE


def test_test_items_stats_is_unchanged() -> None:
    parameters = tuple(
        inspect.signature(
            assessment_stats_router.test_items_stats
        ).parameters
    )

    assert parameters == _STATS_PARAMETERS
    stats_module = vars(assessment_stats_router)

    assert stats_module["resolved_scope"] is resolved_folder_id
