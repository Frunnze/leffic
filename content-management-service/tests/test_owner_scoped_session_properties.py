import uuid

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from features.study_units.assessment_queries import ongoing_session
from shared.models import TestSession
from tests.session_ownership_support import DONE, ONGOING
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import in_memory_sessions

_EXAMPLES = settings(max_examples=25, deadline=None)


@_EXAMPLES
@given(st.uuids(), st.uuids(), st.uuids())
def test_ongoing_session_property_never_hands_over_a_foreign_row(
    owner: uuid.UUID, stranger: uuid.UUID, origin: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    sessions = in_memory_sessions()

    with sessions() as session:
        theirs = opened_test_session(session, stranger, origin)
        opened = ongoing_session(session, str(owner), str(origin))

    assert opened != str(theirs)


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_ongoing_session_property_stamps_the_calling_owner(
    owner: uuid.UUID, origin: uuid.UUID
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        opened = ongoing_session(session, str(owner), str(origin))
        created = session.get(TestSession, uuid.UUID(opened))

        assert created is not None
        assert str(created.user_id) == str(owner)


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_ongoing_session_property_never_revives_a_finished_session(
    owner: uuid.UUID, origin: uuid.UUID
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        finished = opened_test_session(session, owner, origin, DONE)
        opened = ongoing_session(session, str(owner), str(origin))
        reopened = session.get(TestSession, uuid.UUID(opened))

        assert opened != str(finished)
        assert reopened is not None
        assert reopened.status == ONGOING


@_EXAMPLES
@given(st.uuids(), st.uuids(), st.uuids())
def test_ongoing_session_property_keeps_every_origin_apart(
    owner: uuid.UUID, origin: uuid.UUID, other_origin: uuid.UUID
) -> None:
    _ = assume(origin != other_origin)

    sessions = in_memory_sessions()

    with sessions() as session:
        here = ongoing_session(session, str(owner), str(origin))
        there = ongoing_session(session, str(owner), str(other_origin))

    assert here != there
