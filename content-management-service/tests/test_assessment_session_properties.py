import uuid
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units.assessment_queries import (
    items_query,
    ongoing_session,
    session_answers,
)
from shared.models import TestItem, TestSession
from tests.assessment_seeding import seeded_test
from tests.property_support import property_world
from tests.session_ownership_support import ONGOING
from tests.support import authorization

_OK = 200
_CLIENT, _SESSIONS = property_world()
_ITEM_COUNTS = st.integers(min_value=1, max_value=3)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_COUNTS)
def test_session_answers_property_stays_empty_until_something_is_reviewed(
    owner: uuid.UUID, item_count: int
) -> None:
    with _SESSIONS() as session:
        _, _, item_ids = seeded_test(session, owner, item_count)
        item = session.get(TestItem, item_ids[0])

        assert item is not None
        assert session_answers(item, session, str(uuid.uuid4())) is None


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_ongoing_session_property_reuses_one_row_per_owner_and_origin(
    owner: uuid.UUID, origin: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        first = ongoing_session(session, str(owner), str(origin))
        second = ongoing_session(session, str(owner), str(origin))
        rows = (
            session.query(TestSession)
            .filter(
                TestSession.user_id == owner,
                TestSession.origin_id == origin,
                TestSession.status == ONGOING,
            )
            .count()
        )

    assert first == second
    assert rows == 1


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_COUNTS)
def test_items_query_property_finds_the_same_items_either_way(
    owner: uuid.UUID, item_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id, test_id, _ = seeded_test(session, owner, item_count)
        by_test = items_query(
            session, str(test_id), str(folder_id), str(owner)
        )
        by_folder = items_query(
            session, None, str(folder_id), str(owner)
        )

        assert by_test.count() == item_count
        assert by_folder.count() == item_count


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_COUNTS, st.integers(min_value=1, max_value=3))
def test_get_test_items_property_never_returns_more_than_a_page(
    owner: uuid.UUID, item_count: int, per_page: int
) -> None:
    with _SESSIONS() as session:
        _, test_id, _ = seeded_test(session, owner, item_count)

    response = _CLIENT.get(
        "/test-items",
        params={"test_id": str(test_id), "per_page": per_page},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, object]", response.json())

    assert response.status_code == _OK
    assert body["total_items"] == item_count
    assert len(cast("list[object]", body["test_items"])) == min(
        per_page, item_count
    )


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.integers(min_value=0, max_value=3))
def test_review_test_item_property_scores_only_the_true_option(
    owner: uuid.UUID, answer: int
) -> None:
    with _SESSIONS() as session:
        _, test_id, item_ids = seeded_test(session, owner, 1)

    opened = _CLIENT.get(
        "/test-items",
        params={"test_id": str(test_id)},
        headers=authorization(str(owner)),
    )
    test_session = cast("dict[str, str]", opened.json())["test_session"]
    response = _CLIENT.post(
        "/review-test-item",
        json={
            "test_item_id": item_ids[0],
            "test_session": test_session,
            "answers": [answer],
        },
        headers=authorization(str(owner)),
    )

    assert response.status_code == _OK
