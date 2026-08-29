import uuid

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units.assessment_queries import ongoing_session
from shared.models import TestSession
from tests.session_ownership_support import ONGOING
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import in_memory_sessions

_BOTH_SESSIONS = 2


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def test_a_foreign_ongoing_session_is_not_reused(
    sessions: sessionmaker[Session],
) -> None:
    owner = uuid.uuid4()
    stranger = uuid.uuid4()
    origin = uuid.uuid4()

    with sessions() as session:
        theirs = opened_test_session(session, stranger, origin)
        opened = ongoing_session(session, str(owner), str(origin))
        rows = session.query(TestSession).count()

    assert opened != str(theirs)
    assert rows == _BOTH_SESSIONS


def test_a_created_session_records_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owner = uuid.uuid4()
    origin = uuid.uuid4()

    with sessions() as session:
        opened = ongoing_session(session, str(owner), str(origin))
        created = session.get(TestSession, uuid.UUID(opened))

        assert created is not None
        assert str(created.user_id) == str(owner)
        assert str(created.origin_id) == str(origin)
        assert created.status == ONGOING
