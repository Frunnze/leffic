import uuid

from hypothesis import assume, given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.study_units.assessment_router import _upserted_review
from shared.models import TestItemReview
from tests.assessment_seeding import seeded_test
from tests.property_support import property_world
from tests.study_unit_access_support import (
    MISSING_TEST_ITEM_DETAIL,
    NOT_FOUND,
    opened_test_session,
    review_payload,
)
from tests.support import authorization

_CLIENT, _SESSIONS = property_world()
_EXAMPLES = settings(max_examples=25, deadline=None)
_ANSWERS = st.lists(
    st.integers(min_value=0, max_value=3), min_size=1, max_size=3
)
_ACCURACIES = st.integers(min_value=0, max_value=1)
_UPSERTS = st.lists(
    st.tuples(_ANSWERS, _ACCURACIES), min_size=1, max_size=5
)
_ONE_ROW_PER_SESSION = 2


def _seeded_item(
    session: Session, owner: uuid.UUID
) -> tuple[int, uuid.UUID]:
    _, test_id, item_ids = seeded_test(session, owner, 1)

    return item_ids[0], opened_test_session(
        session, owner, test_id
    )


@_EXAMPLES
@given(st.uuids(), _UPSERTS)
def test__upserted_review_property_keeps_one_row_per_session_and_item(
    owner: uuid.UUID, upserts: list[tuple[list[int], int]]
) -> None:
    with _SESSIONS() as session:
        item_id, session_id = _seeded_item(session, owner)

        for answers, accuracy in upserts:
            _upserted_review(
                session, session_id, item_id, list(answers), accuracy
            )
            session.commit()

        stored = (
            session.query(TestItemReview)
            .filter(
                TestItemReview.test_session == session_id,
                TestItemReview.test_item_id == item_id,
            )
            .all()
        )
        last_answers, last_accuracy = upserts[-1]

        assert len(stored) == 1
        assert stored[0].answers == list(last_answers)
        assert stored[0].accuracy == last_accuracy


@_EXAMPLES
@given(st.uuids(), _ANSWERS, _ACCURACIES)
def test__upserted_review_property_keeps_every_session_apart(
    owner: uuid.UUID, answers: list[int], accuracy: int
) -> None:
    with _SESSIONS() as session:
        item_id, first_session = _seeded_item(session, owner)
        second_session = opened_test_session(
            session, owner, uuid.uuid4()
        )

        _upserted_review(
            session, first_session, item_id, list(answers), accuracy
        )
        _upserted_review(
            session, second_session, item_id, list(answers), accuracy
        )
        session.commit()

        stored = (
            session.query(TestItemReview)
            .filter(TestItemReview.test_item_id == item_id)
            .count()
        )

        assert stored == _ONE_ROW_PER_SESSION


@_EXAMPLES
@given(st.uuids(), st.uuids(), _ANSWERS)
def test_review_test_item_property_never_reaches_a_strangers_item(
    owner: uuid.UUID, stranger: uuid.UUID, answers: list[int]
) -> None:
    _ = assume(owner != stranger)

    with _SESSIONS() as session:
        item_id, session_id = _seeded_item(session, owner)

    response = _CLIENT.post(
        "/review-test-item",
        json=review_payload(item_id, session_id, list(answers)),
        headers=authorization(str(stranger)),
    )

    with _SESSIONS() as session:
        assert (
            session.query(TestItemReview)
            .filter(TestItemReview.test_item_id == item_id)
            .count()
            == 0
        )

    assert response.status_code == NOT_FOUND
    assert response.json() == {"detail": MISSING_TEST_ITEM_DETAIL}


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_update_test_item_property_never_reaches_a_strangers_item(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    with _SESSIONS() as session:
        item_id, _ = _seeded_item(session, owner)

    response = _CLIENT.patch(
        "/update-test-item",
        json={"test_item_id": item_id, "content": {"question": "edited"}},
        headers=authorization(str(stranger)),
    )

    assert response.status_code == NOT_FOUND
    assert response.json() == {"detail": MISSING_TEST_ITEM_DETAIL}
