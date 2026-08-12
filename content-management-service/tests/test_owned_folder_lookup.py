import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from shared.folder_access import owned_folder
from tests.access_support import (
    HOME_ID,
    MISSING_FOLDER,
    MISSING_UNIT,
    OTHER_HOME_ID,
    seeded_content,
)
from tests.support import USER_ID, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def test_an_owned_folder_is_returned_to_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        folder = owned_folder(
            session, USER_ID, owned.folder_id, MISSING_FOLDER
        )

    assert str(folder.id) == owned.folder_id
    assert folder.name == "Sub"


def test_an_owned_home_folder_is_returned_to_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        folder = owned_folder(
            session, USER_ID, owned.home_id, MISSING_FOLDER
        )

    assert str(folder.id) == str(folder.user_id)


def test_a_folder_owned_by_another_user_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    theirs = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder(
            session, USER_ID, theirs.folder_id, MISSING_FOLDER
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_FOLDER


def test_a_home_folder_of_another_user_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    theirs = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder(session, USER_ID, theirs.home_id, MISSING_FOLDER)

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_FOLDER


def test_a_folder_that_was_never_created_is_reported_as_missing(
    sessions: sessionmaker[Session],
) -> None:
    _ = seeded_content(sessions, HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder(
            session, USER_ID, str(uuid.uuid4()), MISSING_FOLDER
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_FOLDER


def test_a_malformed_folder_id_is_reported_as_missing(
    sessions: sessionmaker[Session],
) -> None:
    _ = seeded_content(sessions, HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder(session, USER_ID, "home", MISSING_FOLDER)

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_FOLDER


def test_the_detail_the_caller_passes_is_the_detail_reported(
    sessions: sessionmaker[Session],
) -> None:
    theirs = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder(session, USER_ID, theirs.folder_id, MISSING_UNIT)

    assert raised.value.detail == MISSING_UNIT


def test_a_deck_id_never_resolves_to_a_folder(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_folder(session, USER_ID, owned.deck_id, MISSING_FOLDER)

    assert raised.value.status_code == 404
