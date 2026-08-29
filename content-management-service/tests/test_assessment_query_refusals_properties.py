import uuid

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units.assessment_queries import (
    MISSING_SESSION,
    MISSING_TEST,
    items_query,
    session_answers,
)
from shared.models import TestItem
from tests.assessment_seeding import (
    NOT_FOUND,
    UNREADABLE,
    UNREADABLE_ID,
    seeded_test,
)
from tests.property_support import property_world

_, _SESSIONS = property_world()


@settings(max_examples=25, deadline=None)
@given(st.uuids(), UNREADABLE)
def test_session_answers_property_refuses_a_session_it_cannot_read(
    owner: uuid.UUID, test_session: str
) -> None:
    with _SESSIONS() as session:
        _, _, item_ids = seeded_test(session, owner, 1)
        item = session.get(TestItem, item_ids[0])

        assert item is not None

        with pytest.raises(HTTPException) as raised:
            _ = session_answers(item, session, test_session)

    assert raised.value.status_code == NOT_FOUND
    assert raised.value.detail == MISSING_SESSION


@settings(max_examples=25, deadline=None)
@given(UNREADABLE_ID)
def test_items_query_property_refuses_a_test_it_cannot_read(
    test_id: str,
) -> None:
    with _SESSIONS() as session, pytest.raises(HTTPException) as raised:
        _ = items_query(
            session, test_id, str(uuid.uuid4()), str(uuid.uuid4())
        )

    assert raised.value.status_code == NOT_FOUND
    assert raised.value.detail == MISSING_TEST
