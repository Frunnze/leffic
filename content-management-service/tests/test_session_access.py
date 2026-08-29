import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import assessment_queries
from features.study_units.session_access import owned_session_for_origin
from tests.session_ownership_support import (
    MISSING_SESSION_DETAIL,
    NOT_FOUND,
)
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import in_memory_sessions

_UNPARSEABLE = "not-a-uuid"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _refusal(
    session: Session, user_id: uuid.UUID, session_id: str, origin_id: str
) -> tuple[int, str]:
    with pytest.raises(HTTPException) as refused:
        _ = owned_session_for_origin(
            session,
            str(user_id),
            session_id,
            origin_id,
            MISSING_SESSION_DETAIL,
        )

    return refused.value.status_code, str(refused.value.detail)


def test_module_exists_and_queries_hold_no_ownership_check() -> None:
    ownership_names = [
        name for name in dir(assessment_queries) if "owned" in name
    ]

    assert callable(owned_session_for_origin)
    assert ownership_names == []


def test_owned_scope_is_gone() -> None:
    assert hasattr(assessment_queries, "owned_scope") is False


def test_the_resolver_returns_the_callers_session_for_the_matching_origin(
    sessions: sessionmaker[Session],
) -> None:
    owner = uuid.uuid4()
    origin = uuid.uuid4()

    with sessions() as session:
        session_id = opened_test_session(session, owner, origin)
        resolved = owned_session_for_origin(
            session,
            str(owner),
            str(session_id),
            str(origin),
            MISSING_SESSION_DETAIL,
        )

        assert resolved.id == session_id
        assert resolved.user_id == owner


def test_every_resolver_refusal_is_the_same_404(
    sessions: sessionmaker[Session],
) -> None:
    owner = uuid.uuid4()
    stranger = uuid.uuid4()
    origin = uuid.uuid4()

    with sessions() as session:
        mine = opened_test_session(session, owner, origin)
        theirs = opened_test_session(session, stranger, origin)
        elsewhere = opened_test_session(session, owner, uuid.uuid4())
        refusals = {
            _refusal(session, owner, _UNPARSEABLE, str(origin)),
            _refusal(session, owner, str(uuid.uuid4()), str(origin)),
            _refusal(session, owner, str(theirs), str(origin)),
            _refusal(
                session, owner, str(elsewhere), str(origin)
            ),
            _refusal(session, owner, str(mine), str(uuid.uuid4())),
        }

    assert refusals == {(NOT_FOUND, MISSING_SESSION_DETAIL)}
