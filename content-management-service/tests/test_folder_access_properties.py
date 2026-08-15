import uuid

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.folder_access import (
    MISSING_FOLDER,
    ensured_home_folder,
    owned_folder,
    owned_folder_id,
    resolved_folder_id,
)
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_NOT_FOUND = 404
_HOME = "home"
_SESSIONS = in_memory_sessions()
_UNPARSABLE = st.sampled_from(
    ["", " ", "not-a-uuid", "home-folder", "../etc", "null"]
)


@settings(max_examples=50)
@given(st.uuids())
def test_resolved_folder_id_property_reads_home_as_the_caller(
    user_id: uuid.UUID,
) -> None:
    assert resolved_folder_id(str(user_id), _HOME) == str(user_id)


@settings(max_examples=50)
@given(st.uuids(), st.uuids())
def test_resolved_folder_id_property_passes_any_other_folder_through(
    user_id: uuid.UUID, folder_id: uuid.UUID
) -> None:
    assert resolved_folder_id(str(user_id), str(folder_id)) == str(folder_id)


@settings(max_examples=50)
@given(st.uuids(), st.one_of(st.none(), _UNPARSABLE))
def test_resolved_folder_id_property_refuses_anything_unparsable(
    user_id: uuid.UUID, folder_id: str | None
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = resolved_folder_id(str(user_id), folder_id)

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == MISSING_FOLDER


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_owned_folder_id_property_never_resolves_a_strangers_folder(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        assert owned_folder_id(session, str(owner), str(folder_id)) == str(
            folder_id
        )

        with pytest.raises(HTTPException) as raised:
            _ = owned_folder_id(session, str(stranger), str(folder_id))

    assert raised.value.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_owned_folder_property_never_hands_over_a_strangers_folder(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        mine = owned_folder(
            session, str(owner), str(folder_id), MISSING_FOLDER
        )

        assert mine.id == folder_id

        with pytest.raises(HTTPException) as raised:
            _ = owned_folder(
                session, str(stranger), str(folder_id), MISSING_FOLDER
            )

    assert raised.value.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_ensured_home_folder_property_creates_a_home_only_once(
    user_id: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        first = ensured_home_folder(session, str(user_id))
        second = ensured_home_folder(session, str(user_id))

        assert first.id == user_id
        assert second.id == first.id
        assert second.name == first.name
