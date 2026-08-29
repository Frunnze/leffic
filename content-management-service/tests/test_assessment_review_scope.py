import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import TestItemReview
from tests.access_support import scoped_client
from tests.session_ownership_support import (
    CORRECT_ANSWER,
    DONE,
    NOT_FOUND,
    OK,
    OwnedQuiz,
    review_body,
    seeded_quiz,
)
from tests.study_unit_access_support import (
    MISSING_TEST_ITEM_DETAIL,
    opened_test_session,
)
from tests.support import USER_ID, authorization, in_memory_sessions

_CALLER = uuid.UUID(USER_ID)
_SAVED = {"msg": "Saved!"}


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


def _posted_review(
    client: TestClient,
    test_item_id: int,
    test_session: uuid.UUID | str,
) -> tuple[int, dict[str, str]]:
    response = client.post(
        "/review-test-item",
        json=review_body(test_item_id, test_session, CORRECT_ANSWER),
        headers=authorization(),
    )

    return response.status_code, cast(
        "dict[str, str]", response.json()
    )


def _refused_attempts(
    sessions: sessionmaker[Session], owned: OwnedQuiz
) -> tuple[tuple[int, str], ...]:
    with sessions() as session:
        stranger_quiz = seeded_quiz(session, uuid.uuid4())
        mine = opened_test_session(session, _CALLER, owned.test_id)
        theirs = opened_test_session(
            session, stranger_quiz.owner, owned.test_id
        )
        unrelated = opened_test_session(
            session, _CALLER, uuid.uuid4()
        )

    return (
        (stranger_quiz.test_item_id, str(mine)),
        (owned.test_item_id, str(uuid.uuid4())),
        (owned.test_item_id, str(theirs)),
        (owned.test_item_id, str(unrelated)),
    )


def _refused_reviews(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedQuiz,
) -> set[tuple[int, str]]:
    refusals: set[tuple[int, str]] = set()

    for test_item_id, supplied in _refused_attempts(sessions, owned):
        code, body = _posted_review(client, test_item_id, supplied)
        refusals.add((code, body.get("detail", "")))

    return refusals


def _stored_reviews(sessions: sessionmaker[Session]) -> int:
    with sessions() as session:
        return session.query(TestItemReview).count()


def test_the_owner_can_still_save_an_answer(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        mine = opened_test_session(session, _CALLER, owned.test_id)

    code, body = _posted_review(client, owned.test_item_id, mine)

    assert code == OK
    assert body == _SAVED
    assert _stored_reviews(sessions) == 1


def test_a_test_scoped_session_accepts_its_own_item(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        mine = opened_test_session(session, _CALLER, owned.test_id)

    code, body = _posted_review(client, owned.test_item_id, mine)

    with sessions() as session:
        review = session.query(TestItemReview).one()

    assert code == OK
    assert body == _SAVED
    assert review.test_session == mine


def test_a_folder_scoped_session_accepts_a_nested_item(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        mine = opened_test_session(session, _CALLER, owned.folder_id)

    code, body = _posted_review(client, owned.test_item_id, mine)

    assert code == OK
    assert body == _SAVED


def test_every_review_refusal_is_the_same_404(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    refusals = _refused_reviews(client, sessions, owned)

    assert refusals == {(NOT_FOUND, MISSING_TEST_ITEM_DETAIL)}


def test_a_refused_review_persists_nothing(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    _ = _refused_reviews(client, sessions, owned)

    assert _stored_reviews(sessions) == 0


def test_a_done_session_still_accepts_an_answer(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedQuiz
) -> None:
    with sessions() as session:
        finished = opened_test_session(
            session, _CALLER, owned.test_id, DONE
        )

    code, body = _posted_review(client, owned.test_item_id, finished)

    assert code == OK
    assert body == _SAVED
