import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from shared.folder_access import owned_folder_id
from shared.models import Folder
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions

_NOT_FOUND = 404

_MISSING_FOLDER = "Folder does not exist!"
_OWNED_ID = uuid.UUID("6f1c7d4e-0000-4000-8000-0000000000aa")


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _store_folder(
    sessions: sessionmaker[Session], folder_id: uuid.UUID, owner: str
) -> None:
    with sessions() as session:
        session.add(Folder(id=folder_id, name="F", user_id=uuid.UUID(owner)))
        session.commit()


def test_an_owned_folder_resolves_to_its_own_id(
    sessions: sessionmaker[Session],
) -> None:
    _store_folder(sessions, _OWNED_ID, USER_ID)

    with sessions() as session:
        resolved = owned_folder_id(session, USER_ID, str(_OWNED_ID))

    assert resolved == str(_OWNED_ID)


def test_the_home_alias_resolves_to_the_user_id(
    sessions: sessionmaker[Session],
) -> None:
    _store_folder(sessions, uuid.UUID(USER_ID), USER_ID)

    with sessions() as session:
        resolved = owned_folder_id(session, USER_ID, "home")

    assert resolved == USER_ID


def test_a_folder_owned_by_another_user_is_rejected(
    sessions: sessionmaker[Session],
) -> None:
    _store_folder(sessions, _OWNED_ID, OTHER_USER_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder_id(session, USER_ID, str(_OWNED_ID))

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == _MISSING_FOLDER


def test_another_folder_id_is_rejected_even_when_the_user_owns_one(
    sessions: sessionmaker[Session],
) -> None:
    _store_folder(sessions, _OWNED_ID, USER_ID)
    unknown_id = uuid.UUID("6f1c7d4e-0000-4000-8000-0000000000bb")

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder_id(session, USER_ID, str(unknown_id))

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == _MISSING_FOLDER


def test_a_missing_folder_id_is_rejected(
    sessions: sessionmaker[Session],
) -> None:
    _store_folder(sessions, _OWNED_ID, USER_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder_id(session, USER_ID, None)

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == _MISSING_FOLDER
