from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.file_system import file_storage
from tests.access_support import (
    HOME_ID,
    MISSING_FOLDER,
    OTHER_HOME_ID,
    PROTECTED_HOME,
    OwnedContent,
    delete_unit,
    scoped_client,
    seeded_content,
    surviving_folder_ids,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def theirs(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, OTHER_HOME_ID)


def _delete_folder(
    client: TestClient, folder_id: str, headers: dict[str, str]
) -> tuple[int, dict[str, str]]:
    return delete_unit(
        client, "/delete-folder/", "folder_id", folder_id, headers
    )


def test_another_users_folder_cannot_be_deleted(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    theirs: OwnedContent,
) -> None:
    assert theirs.folder_id

    code, body = _delete_folder(
        client, owned.folder_id, authorization(OTHER_USER_ID)
    )

    assert code == 404
    assert body["detail"] == MISSING_FOLDER
    assert owned.folder_id in surviving_folder_ids(sessions)


def test_another_users_home_folder_is_reported_as_missing(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    theirs: OwnedContent,
) -> None:
    assert theirs.home_id

    code, body = _delete_folder(
        client, owned.home_id, authorization(OTHER_USER_ID)
    )

    assert code == 404
    assert body["detail"] == MISSING_FOLDER
    assert owned.home_id in surviving_folder_ids(sessions)


def test_your_own_home_folder_cannot_be_deleted(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = _delete_folder(client, owned.home_id, authorization())

    assert code == 422
    assert body["detail"] == PROTECTED_HOME
    assert owned.home_id in surviving_folder_ids(sessions)


def test_deleting_a_folder_without_a_token_is_refused(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, _body = _delete_folder(client, owned.folder_id, {})

    assert code == 401
    assert owned.folder_id in surviving_folder_ids(sessions)


def test_an_owner_still_deletes_their_own_subfolder(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = _delete_folder(client, owned.folder_id, authorization())

    assert code == 200
    assert body == {"msg": "Folder deleted!"}
    assert surviving_folder_ids(sessions) == {owned.home_id}


def test_another_users_folder_keeps_its_files_in_storage(
    client: TestClient,
    owned: OwnedContent,
    theirs: OwnedContent,
    tmp_path: Path,
) -> None:
    assert theirs.folder_id
    document = tmp_path / f"{owned.file_id}.pdf"
    _ = document.write_bytes(b"payload")

    with mock.patch.object(
        file_storage, "_FILES_DIRECTORY", str(tmp_path)
    ):
        code, _body = _delete_folder(
            client, owned.folder_id, authorization(OTHER_USER_ID)
        )

    assert code == 404
    assert document.exists()
