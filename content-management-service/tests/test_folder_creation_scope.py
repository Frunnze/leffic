import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import Folder, Note
from tests.access_support import (
    HOME_ID,
    MISSING_FOLDER,
    OTHER_HOME_ID,
    scoped_client,
)
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    authorization,
    in_memory_sessions,
)

_NOT_FOUND = 404
_OK = 200
_EXPECTED_FOREIGN_FOLDER_COUNT = 2


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def foreign_folder_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.add(
            Folder(id=OTHER_HOME_ID, name="Home", user_id=OTHER_HOME_ID)
        )
        session.commit()
        folder = Folder(
            parent_id=OTHER_HOME_ID, name="Theirs", user_id=OTHER_HOME_ID
        )
        session.add(folder)
        session.commit()

        return str(folder.id)


def _create_folder(
    client: TestClient, parent_folder_id: str, user_id: str
) -> tuple[int, dict[str, str]]:
    response = client.post(
        "/create-folder",
        json={"parent_folder_id": parent_folder_id, "folder_name": "Mine"},
        headers=authorization(user_id),
    )

    return response.status_code, cast("dict[str, str]", response.json())


def test_a_folder_cannot_be_planted_in_another_users_folder(
    client: TestClient, foreign_folder_id: str
) -> None:
    code, body = _create_folder(client, foreign_folder_id, USER_ID)

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FOLDER


def test_planting_a_foreign_folder_creates_no_row(
    client: TestClient,
    sessions: sessionmaker[Session],
    foreign_folder_id: str,
) -> None:
    _ = _create_folder(client, foreign_folder_id, USER_ID)

    with sessions() as session:
        planted = session.query(Folder).filter_by(user_id=HOME_ID).count()

    assert planted == 1


def test_a_folder_cannot_be_planted_in_another_users_home(
    client: TestClient, foreign_folder_id: str
) -> None:
    assert foreign_folder_id

    code, body = _create_folder(client, OTHER_USER_ID, USER_ID)

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FOLDER


def test_a_missing_parent_folder_is_reported(client: TestClient) -> None:
    code, body = _create_folder(client, str(uuid.uuid4()), USER_ID)

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FOLDER


def test_a_folder_is_created_in_a_folder_you_own(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()
        owned = Folder(parent_id=HOME_ID, name="Mine", user_id=HOME_ID)
        session.add(owned)
        session.commit()
        owned_id = str(owned.id)

    code, body = _create_folder(client, owned_id, USER_ID)

    assert code == _OK
    assert body["parent_folder_id"] == owned_id


def test_a_folder_is_created_under_home_when_home_is_missing(
    client: TestClient,
) -> None:
    code, body = _create_folder(client, "home", USER_ID)

    assert code == _OK
    assert body["parent_folder_id"] == USER_ID


def test_deleting_your_folder_cannot_cascade_into_foreign_content(
    client: TestClient,
    sessions: sessionmaker[Session],
    foreign_folder_id: str,
) -> None:
    assert foreign_folder_id

    with sessions() as session:
        mine = Folder(parent_id=HOME_ID, name="Mine", user_id=HOME_ID)
        session.add(mine)
        session.commit()
        mine_id = str(mine.id)

    planted, _ = _create_folder(client, mine_id, OTHER_USER_ID)

    with sessions() as session:
        session.add(
            Note(
                folder_id=OTHER_HOME_ID,
                name="Theirs",
                content="secret",
                type="general",
            )
        )
        session.commit()

    removed = client.request(
        "DELETE",
        "/delete-folder/",
        params={"folder_id": mine_id},
        headers=authorization(),
    )

    with sessions() as session:
        foreign_notes = session.query(Note).count()
        foreign_folders = (
            session.query(Folder).filter_by(user_id=OTHER_HOME_ID).count()
        )

    assert planted == _NOT_FOUND
    assert removed.status_code == _OK
    assert foreign_notes == 1
    assert foreign_folders == _EXPECTED_FOREIGN_FOLDER_COUNT
