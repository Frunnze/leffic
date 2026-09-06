import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from shared.folder_access import MISSING_FOLDER, ensured_home_folder
from shared.models import Folder
from tests.folder_owner_support import (
    FOREIGN_HOME_ID,
    HOME_ID,
    HOME_NAME,
    added_home,
)
from tests.support import USER_ID, in_memory_sessions

_NOT_FOUND = 404


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _seeded_foreign_home(sessions: sessionmaker[Session]) -> None:
    with sessions() as session:
        session.add(
            Folder(id=HOME_ID, name=HOME_NAME, user_id=FOREIGN_HOME_ID)
        )
        session.commit()


def test_ensured_home_folder_refuses_a_foreign_home(
    sessions: sessionmaker[Session],
) -> None:
    _seeded_foreign_home(sessions)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = ensured_home_folder(session, USER_ID)

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == MISSING_FOLDER


def test_a_refused_home_lookup_creates_no_row(
    sessions: sessionmaker[Session],
) -> None:
    _seeded_foreign_home(sessions)

    with sessions() as session, pytest.raises(HTTPException):
        _ = ensured_home_folder(session, USER_ID)

    with sessions() as session:
        assert session.query(Folder).count() == 1


def test_ensured_home_folder_still_creates_a_missing_home(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        created = ensured_home_folder(session, USER_ID)

        assert created.id == HOME_ID
        assert created.user_id == HOME_ID
        assert created.name == HOME_NAME


def test_ensured_home_folder_returns_the_existing_home(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        added_home(session, HOME_ID)

    with sessions() as session:
        found = ensured_home_folder(session, USER_ID)

        assert found.id == HOME_ID
        assert session.query(Folder).count() == 1
