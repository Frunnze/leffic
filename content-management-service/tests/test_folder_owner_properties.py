import uuid

import pytest
from fastapi import HTTPException
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from features.file_system.folder_router import _files_storage_ids
from shared.folder_access import MISSING_FOLDER, ensured_home_folder
from shared.models import File, Folder
from tests.folder_owner_support import (
    FOREIGN_HOME_ID,
    HOME_ID,
    HOME_NAME,
    added_descendant_chain,
    added_folder,
    returned_subtree,
)
from tests.support import USER_ID, in_memory_sessions

_NOT_FOUND = 404
_EXTENSION = "pdf"
_DEPTHS = st.integers(min_value=0, max_value=5)


@settings(max_examples=25, deadline=None)
@given(_DEPTHS, st.integers(min_value=1, max_value=4))
def test_subfolder_ids_property_stops_at_the_first_foreign_folder(
    owned_depth: int, foreign_depth: int
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        root_id = added_folder(session, HOME_ID, None, "root")
        owned = added_descendant_chain(session, HOME_ID, root_id, owned_depth)
        graft_parent = owned[-1] if owned else root_id
        foreign_id = added_folder(
            session, FOREIGN_HOME_ID, graft_parent, "theirs"
        )
        beyond = added_descendant_chain(
            session, HOME_ID, foreign_id, foreign_depth
        )

    returned = returned_subtree(sessions, root_id, USER_ID)

    assert returned == {root_id, *owned}
    assert foreign_id not in returned
    assert returned & set(beyond) == set()


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_ensured_home_folder_property_refuses_every_foreign_home(
    caller: uuid.UUID, other_owner: uuid.UUID
) -> None:
    _ = assume(caller != other_owner)
    sessions = in_memory_sessions()

    with sessions() as session:
        session.add(Folder(id=caller, name=HOME_NAME, user_id=other_owner))
        session.commit()

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = ensured_home_folder(session, str(caller))

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == MISSING_FOLDER


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.integers(min_value=1, max_value=4))
def test_ensured_home_folder_property_creates_at_most_one_home_row(
    caller: uuid.UUID, lookups: int
) -> None:
    sessions = in_memory_sessions()

    for _ in range(lookups):
        with sessions() as session:
            _ = ensured_home_folder(session, str(caller))

    with sessions() as session:
        assert session.query(Folder).count() == 1


@settings(max_examples=20, deadline=None)
@given(st.integers(min_value=1, max_value=3))
def test__files_storage_ids_property_names_only_the_owners_files(
    foreign_file_count: int,
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        root_id = added_folder(session, HOME_ID, None, "root")
        foreign_id = added_folder(
            session, FOREIGN_HOME_ID, root_id, "theirs"
        )
        owned_file = File(
            folder_id=root_id, name="mine", extension=_EXTENSION
        )
        session.add(owned_file)

        for index in range(foreign_file_count):
            session.add(
                File(
                    folder_id=foreign_id,
                    name=f"theirs-{index}",
                    extension=_EXTENSION,
                )
            )

        session.commit()
        expected = [f"{owned_file.id}.{_EXTENSION}"]

    with sessions() as session:
        named = _files_storage_ids(session, str(root_id), USER_ID)

    assert named == expected
