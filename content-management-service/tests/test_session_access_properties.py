import uuid

import pytest
from fastapi import HTTPException
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from features.study_units.session_access import (
    _refuse,
    owned_session,
    owned_session_for_origin,
)
from tests.session_ownership_support import NOT_FOUND
from tests.study_unit_access_support import (
    opened_test_session,
)
from tests.support import in_memory_sessions

_EXAMPLES = settings(max_examples=25, deadline=None)
_DETAILS = st.text(min_size=1, max_size=40)


def _is_not_a_uuid(spelling: str) -> bool:
    try:
        _ = uuid.UUID(spelling)
    except ValueError:
        return True

    return False


_UNPARSEABLE = st.text(max_size=12).filter(_is_not_a_uuid)


@_EXAMPLES
@given(st.uuids(), st.uuids(), st.uuids())
def test_owned_session_for_origin_property_never_returns_a_foreign_session(
    owner: uuid.UUID, stranger: uuid.UUID, origin: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    sessions = in_memory_sessions()

    with sessions() as session:
        theirs = opened_test_session(session, stranger, origin)

        with pytest.raises(HTTPException):
            _ = owned_session_for_origin(
                session, str(owner), str(theirs), str(origin), "gone"
            )


@_EXAMPLES
@given(st.uuids(), st.uuids(), st.uuids())
def test_owned_session_for_origin_property_never_returns_another_origin(
    owner: uuid.UUID, origin: uuid.UUID, asserted_origin: uuid.UUID
) -> None:
    _ = assume(origin != asserted_origin)

    sessions = in_memory_sessions()

    with sessions() as session:
        mine = opened_test_session(session, owner, origin)

        with pytest.raises(HTTPException):
            _ = owned_session_for_origin(
                session,
                str(owner),
                str(mine),
                str(asserted_origin),
                "gone",
            )


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_owned_session_for_origin_property_returns_the_row_it_was_asked_for(
    owner: uuid.UUID, origin: uuid.UUID
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        mine = opened_test_session(session, owner, origin)
        resolved = owned_session_for_origin(
            session, str(owner), str(mine), str(origin), "gone"
        )

        assert resolved.id == mine
        assert str(resolved.user_id) == str(owner)
        assert str(resolved.origin_id) == str(origin)


@_EXAMPLES
@given(st.uuids(), st.uuids(), _DETAILS)
def test_owned_session_for_origin_property_echoes_the_detail_it_was_given(
    owner: uuid.UUID, origin: uuid.UUID, missing_detail: str
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session, pytest.raises(HTTPException) as refused:
        _ = owned_session_for_origin(
            session,
            str(owner),
            str(uuid.uuid4()),
            str(origin),
            missing_detail,
        )

    assert refused.value.status_code == NOT_FOUND
    assert refused.value.detail == missing_detail


@_EXAMPLES
@given(st.uuids(), st.uuids(), _UNPARSEABLE)
def test_owned_session_for_origin_property_refuses_every_unparseable_id(
    owner: uuid.UUID, origin: uuid.UUID, spelling: str
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session, pytest.raises(HTTPException) as refused:
        _ = owned_session_for_origin(
            session, str(owner), spelling, str(origin), "gone"
        )

    assert refused.value.status_code == NOT_FOUND


@_EXAMPLES
@given(st.uuids(), st.uuids(), st.uuids())
def test_owned_session_property_never_returns_a_foreign_session(
    owner: uuid.UUID, stranger: uuid.UUID, origin: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    sessions = in_memory_sessions()

    with sessions() as session:
        theirs = opened_test_session(session, stranger, origin)

        with pytest.raises(HTTPException):
            _ = owned_session(session, str(owner), str(theirs), "gone")


@_EXAMPLES
@given(_DETAILS)
def test__refuse_property_always_raises_the_detail_it_was_given(
    missing_detail: str,
) -> None:
    with pytest.raises(HTTPException) as refused:
        _refuse(missing_detail)

    assert refused.value.status_code == NOT_FOUND
    assert refused.value.detail == missing_detail
