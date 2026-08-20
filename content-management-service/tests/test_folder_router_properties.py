import uuid
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.file_system.folder_router import (
    _available_folder_name,
    _files_storage_ids,
    _home_folder_response,
    _owned_parent_id,
)
from shared.folder_access import ensured_home_folder
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world
from tests.support import authorization

_OK = 200
_UNPROCESSABLE = 422
_NOT_FOUND = 404
_HOME = "home"
_CLIENT, _SESSIONS = property_world()
_NAMES = st.text(alphabet="abcdefg ", min_size=1, max_size=8)
_SIBLING_COUNTS = st.integers(min_value=0, max_value=3)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _NAMES, _SIBLING_COUNTS)
def test__available_folder_name_property_numbers_each_repeat_in_turn(
    owner: uuid.UUID, folder_name: str, sibling_count: int
) -> None:
    with _SESSIONS() as session:
        parent_id = seeded_folder(session, owner, {})
        chosen = [
            _created_child(session, owner, parent_id, folder_name)
            for _ in range(sibling_count + 1)
        ]

    assert chosen[0] == folder_name
    assert chosen[-1] == (
        folder_name
        if sibling_count == 0
        else f"{folder_name} {sibling_count + 1}"
    )


def _created_child(
    session: Session, owner: uuid.UUID, parent_id: uuid.UUID, name: str
) -> str:
    chosen = _available_folder_name(session, str(parent_id), name)
    _ = _CLIENT.post(
        "/create-folder",
        json={"parent_folder_id": str(parent_id), "folder_name": chosen},
        headers=authorization(str(owner)),
    )
    session.expire_all()

    return chosen


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__owned_parent_id_property_reads_home_as_the_callers_own_folder(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        resolved = _owned_parent_id(session, str(owner), _HOME)

        assert resolved == str(owner)
        assert ensured_home_folder(session, str(owner)).id == owner


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _NAMES)
def test_create_folder_property_answers_with_the_folder_it_made(
    owner: uuid.UUID, folder_name: str
) -> None:
    response = _CLIENT.post(
        "/create-folder",
        json={"parent_folder_id": _HOME, "folder_name": folder_name},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _OK
    assert body["parent_folder_id"] == str(owner)
    assert uuid.UUID(body["folder_id"])


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.integers(min_value=0, max_value=3))
def test__files_storage_ids_property_names_one_id_per_stored_file(
    owner: uuid.UUID, file_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {"file": file_count})
        stored = _files_storage_ids(session, str(folder_id))

    assert len(stored) == file_count
    assert all(name.endswith(".pdf") for name in stored)


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_delete_folder_property_always_protects_the_home_folder(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        _ = ensured_home_folder(session, str(owner))

    refused = _CLIENT.delete(
        "/delete-folder/",
        params={"folder_id": str(owner)},
        headers=authorization(str(owner)),
    )

    assert refused.status_code == _UNPROCESSABLE


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_access_folder_property_never_names_a_strangers_folder(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

    response = _CLIENT.get(
        "/access-folder/",
        params={"folder_id": str(folder_id)},
        headers=authorization(str(stranger)),
    )
    body = cast("dict[str, object]", response.json())

    assert body["parent_folder_name"] == "Home"
    assert body["content"] == []


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__home_folder_response_property_always_describes_a_home(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        response = _home_folder_response(session, str(owner))

    assert response.status_code == _OK
    assert b'"parent_folder_name":"Home"' in bytes(response.body)
