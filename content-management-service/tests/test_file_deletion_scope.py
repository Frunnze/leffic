import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared import file_storage
from shared.models import File
from tests.access_support import (
    HOME_ID,
    MISSING_FILE,
    OTHER_HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
    surviving_ids,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions

_NOT_FOUND = 404
_OK = 200
_UNAUTHORIZED = 401


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
def intruder(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


def _stored_document(directory: Path, file_id: str) -> Path:
    document = directory / f"{file_id}.pdf"
    _ = document.write_bytes(b"payload")

    return document


def _delete_file(
    client: TestClient, file_id: str, headers: dict[str, str], directory: Path
) -> tuple[int, dict[str, str]]:
    with mock.patch.object(file_storage, "_FILES_DIRECTORY", str(directory)):
        response = client.request(
            "DELETE",
            "/delete-file/",
            params={"file_id": file_id},
            headers=headers,
        )

    return response.status_code, cast("dict[str, str]", response.json())


def test_another_users_file_cannot_be_deleted(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
    tmp_path: Path,
) -> None:
    _ = _stored_document(tmp_path, owned.file_id)

    code, body = _delete_file(client, owned.file_id, intruder, tmp_path)

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FILE
    assert owned.file_id in surviving_ids(sessions, File)


def test_another_users_file_stays_in_storage(
    client: TestClient,
    owned: OwnedContent,
    intruder: dict[str, str],
    tmp_path: Path,
) -> None:
    document = _stored_document(tmp_path, owned.file_id)

    _ = _delete_file(client, owned.file_id, intruder, tmp_path)

    assert document.exists()


def test_deleting_a_file_without_a_token_is_refused(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    tmp_path: Path,
) -> None:
    document = _stored_document(tmp_path, owned.file_id)

    code, _body = _delete_file(client, owned.file_id, {}, tmp_path)

    assert code == _UNAUTHORIZED
    assert document.exists()
    assert owned.file_id in surviving_ids(sessions, File)


def test_an_owner_still_deletes_their_own_file(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    tmp_path: Path,
) -> None:
    document = _stored_document(tmp_path, owned.file_id)

    code, body = _delete_file(client, owned.file_id, authorization(), tmp_path)

    assert code == _OK
    assert body == {"msg": "File deleted!"}
    assert not document.exists()
    assert surviving_ids(sessions, File) == set()


def test_a_file_that_was_never_created_is_reported_as_missing(
    client: TestClient, owned: OwnedContent, tmp_path: Path
) -> None:
    assert owned.file_id

    code, body = _delete_file(
        client, str(uuid.uuid4()), authorization(), tmp_path
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FILE
