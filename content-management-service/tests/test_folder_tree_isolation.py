from collections.abc import Iterator
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from features.file_system import unit_router
from shared.models import Folder
from tests.access_support import scoped_client
from tests.folder_owner_support import (
    FOREIGN_HOME_ID,
    HOME_ID,
    added_folder,
    added_home,
    added_ownership_chain,
    owners_of,
    returned_subtree,
)
from tests.support import USER_ID, authorization, in_memory_sessions

_UNPROCESSABLE = 422
_CIRCULAR_MOVE = "A folder cannot be moved inside itself!"
_PROPERTY_SESSIONS = in_memory_sessions()


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_a_foreign_child_is_not_in_the_subtree(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        root_id = added_folder(session, HOME_ID, None, "root")
        foreign_id = added_folder(
            session, FOREIGN_HOME_ID, root_id, "theirs"
        )

    assert returned_subtree(sessions, root_id, USER_ID) == {root_id}
    assert foreign_id not in returned_subtree(sessions, root_id, USER_ID)


def test_a_foreign_childs_descendant_is_not_in_the_subtree(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        root_id = added_folder(session, HOME_ID, None, "root")
        foreign_id = added_folder(
            session, FOREIGN_HOME_ID, root_id, "theirs"
        )
        buried_id = added_folder(session, HOME_ID, foreign_id, "buried")

    assert buried_id not in returned_subtree(sessions, root_id, USER_ID)


def test_every_owned_descendant_is_returned(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        root_id = added_folder(session, HOME_ID, None, "root")
        middle_id = added_folder(session, HOME_ID, root_id, "middle")
        deepest_id = added_folder(session, HOME_ID, middle_id, "deepest")

    assert returned_subtree(sessions, root_id, USER_ID) == {
        root_id,
        middle_id,
        deepest_id,
    }


def test_a_foreign_root_returns_nothing(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        foreign_root_id = added_folder(
            session, FOREIGN_HOME_ID, None, "theirs"
        )
        _ = added_folder(session, FOREIGN_HOME_ID, foreign_root_id, "child")

    assert returned_subtree(sessions, foreign_root_id, USER_ID) == set()


@settings(max_examples=25, deadline=None)
@given(st.lists(st.booleans(), min_size=1, max_size=6))
def test_subfolder_ids_property_returns_only_the_requested_owners_folders(
    ownership_flags: list[bool],
) -> None:
    with _PROPERTY_SESSIONS() as session:
        root_id = added_ownership_chain(session, ownership_flags)

    returned = returned_subtree(_PROPERTY_SESSIONS, root_id, USER_ID)

    with _PROPERTY_SESSIONS() as session:
        assert owners_of(session, returned) == {HOME_ID}


def test__move_folder_asks_for_the_callers_subtree(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        added_home(session, HOME_ID)
        moved_id = added_folder(session, HOME_ID, HOME_ID, "moved")
        destination_id = added_folder(session, HOME_ID, HOME_ID, "elsewhere")

    with (
        sessions() as session,
        mock.patch.object(unit_router, "subfolder_ids") as asked,
    ):
        asked.return_value = select(Folder.id).where(Folder.id.is_(None))
        unit_router._move_folder(
            session, USER_ID, str(moved_id), str(destination_id)
        )

    asked.assert_called_once_with(str(moved_id), USER_ID)


def test_moving_a_folder_into_its_own_descendant_is_still_refused(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        added_home(session, HOME_ID)
        parent_id = added_folder(session, HOME_ID, HOME_ID, "parent")
        child_id = added_folder(session, HOME_ID, parent_id, "child")

    response = client.patch(
        "/move-unit",
        json={
            "unit_id": str(parent_id),
            "unit_type": "folder",
            "folder_id": str(child_id),
        },
        headers=authorization(),
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _UNPROCESSABLE
    assert body["detail"] == _CIRCULAR_MOVE
