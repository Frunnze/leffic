import uuid

import pytest
from fastapi import HTTPException
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from features.study_units.assessment_router import (
    TestItemsQuery,
    _item_payload,
    _owned_origin_id,
    _scoped_session_id,
)
from features.study_units.assessment_stats_router import (
    _count_correct_answers,
)
from features.study_units.session_access import session_covering_item
from shared.models import TestItem
from tests.session_ownership_support import seeded_quiz
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import in_memory_sessions

_EXAMPLES = settings(max_examples=25, deadline=None)
_ITEM_KEYS = {"id", "type", "content", "created_at", "last_answers"}


@_EXAMPLES
@given(st.uuids(), st.uuids(), st.uuids())
def test_session_covering_item_property_never_crosses_owners(
    owner: uuid.UUID, stranger: uuid.UUID, origin: uuid.UUID
) -> None:
    _ = assume(owner != stranger)
    sessions = in_memory_sessions()

    with sessions() as session:
        quiz = seeded_quiz(session, owner)
        theirs = opened_test_session(session, stranger, origin)
        test_item = session.get(TestItem, quiz.test_item_id)

        assert test_item is not None

        with pytest.raises(HTTPException):
            _ = session_covering_item(
                session, str(owner), str(theirs), test_item
            )


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test__owned_origin_id_property_refuses_an_unowned_folder(
    owner: uuid.UUID, folder_id: uuid.UUID
) -> None:
    query = TestItemsQuery(folder_id=str(folder_id))
    sessions = in_memory_sessions()

    with sessions() as session, pytest.raises(HTTPException):
        _ = _owned_origin_id(session, str(owner), query)


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test__scoped_session_id_property_opens_one_session_per_origin(
    owner: uuid.UUID, origin: uuid.UUID
) -> None:
    query = TestItemsQuery()
    sessions = in_memory_sessions()

    with sessions() as session:
        first = _scoped_session_id(
            session, str(owner), query, str(origin)
        )
        second = _scoped_session_id(
            session, str(owner), query, str(origin)
        )

    assert first == second


@_EXAMPLES
@given(st.uuids())
def test__item_payload_property_always_carries_the_same_keys(
    owner: uuid.UUID,
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        quiz = seeded_quiz(session, owner)
        test_item = session.get(TestItem, quiz.test_item_id)

        assert test_item is not None

        payload = _item_payload(
            session, test_item, str(uuid.uuid4())
        )

    assert set(payload) == _ITEM_KEYS


@_EXAMPLES
@given(st.uuids())
def test__count_correct_answers_property_never_scores_empty(
    session_id: uuid.UUID,
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        assert _count_correct_answers(session, session_id) == 0
