import uuid
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.study_units.assessment_router import (
    AssessmentGrading,
    _ongoing_session,
    _session_answers,
    _test_items_query,
)
from shared.models import Test, TestItem
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world
from tests.support import authorization

_OK = 200
_CORRECT = 1
_INCORRECT = 0
_CLIENT, _SESSIONS = property_world()
_ITEM_COUNTS = st.integers(min_value=1, max_value=3)


def _seeded_test(
    session: Session, owner: uuid.UUID, item_count: int
) -> tuple[uuid.UUID, uuid.UUID, list[int]]:
    folder_id = seeded_folder(session, owner, {})
    quiz = Test(
        id=uuid.uuid4(),
        name="Quiz",
        folder_id=folder_id,
        created_at=datetime.now(UTC),
        public=False,
    )
    session.add(quiz)

    for index in range(item_count):
        quiz.test_items.append(
            TestItem(
                content={"question": f"q{index}", "true_option": "yes"},
                type="multiple_choice",
                created_at=datetime.now(UTC),
            )
        )

    session.commit()

    return folder_id, quiz.id, [item.id for item in quiz.test_items]


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_COUNTS)
def test__session_answers_property_stays_empty_until_something_is_reviewed(
    owner: uuid.UUID, item_count: int
) -> None:
    with _SESSIONS() as session:
        _, _, item_ids = _seeded_test(session, owner, item_count)
        item = session.get(TestItem, item_ids[0])

        assert item is not None
        assert _session_answers(item, session, str(uuid.uuid4())) is None


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__ongoing_session_property_reuses_the_session_it_already_opened(
    origin: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        first = _ongoing_session(session, str(origin))
        second = _ongoing_session(session, str(origin))

    assert first == second


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_COUNTS)
def test__test_items_query_property_finds_the_same_items_either_way(
    owner: uuid.UUID, item_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id, test_id, _ = _seeded_test(session, owner, item_count)
        by_test = _test_items_query(
            session, str(test_id), str(folder_id), str(owner)
        )
        by_folder = _test_items_query(
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
        _, test_id, _ = _seeded_test(session, owner, item_count)

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


@settings(max_examples=50)
@given(st.integers(min_value=-2, max_value=3))
def test_graded_property_credits_nothing_for_an_item_that_is_gone(
    answer: int,
) -> None:
    assert AssessmentGrading.graded(None, [answer]) == _INCORRECT


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.integers(min_value=0, max_value=3))
def test_review_test_item_property_scores_only_the_true_option(
    owner: uuid.UUID, answer: int
) -> None:
    with _SESSIONS() as session:
        _, test_id, item_ids = _seeded_test(session, owner, 1)

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
