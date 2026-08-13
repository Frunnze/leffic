import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared import file_storage
from shared.models import File, Folder
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
    surviving_folder_ids,
    surviving_ids,
)
from tests.support import authorization, in_memory_sessions

_EXTENSION = "pdf"


class NestedTree(NamedTuple):
    buried_file_id: str
    sibling_file_id: str
    sibling_folder_id: str


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
def tree(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> NestedTree:
    with sessions() as session:
        middle = Folder(
            parent_id=uuid.UUID(owned.folder_id),
            name="Middle",
            user_id=HOME_ID,
        )
        sibling = Folder(
            parent_id=uuid.UUID(owned.home_id),
            name="Sibling",
            user_id=HOME_ID,
        )
        session.add_all([middle, sibling])
        session.commit()

        deepest = Folder(
            parent_id=middle.id, name="Deepest", user_id=HOME_ID
        )
        session.add(deepest)
        session.commit()

        buried = File(
            folder_id=deepest.id, name="buried", extension=_EXTENSION
        )
        outside = File(
            folder_id=sibling.id, name="outside", extension=_EXTENSION
        )
        session.add_all([buried, outside])
        session.commit()

        return NestedTree(
            buried_file_id=str(buried.id),
            sibling_file_id=str(outside.id),
            sibling_folder_id=str(sibling.id),
        )


def _stored(directory: Path, file_id: str) -> Path:
    document = directory / f"{file_id}.{_EXTENSION}"
    _ = document.write_bytes(b"payload")

    return document


def _delete_folder(
    client: TestClient, folder_id: str, directory: Path
) -> int:
    with mock.patch.object(
        file_storage, "_FILES_DIRECTORY", str(directory)
    ):
        response = client.request(
            "DELETE",
            "/delete-folder/",
            params={"folder_id": folder_id},
            headers=authorization(),
        )

    return response.status_code


def test_a_file_buried_two_levels_down_leaves_storage(
    client: TestClient,
    owned: OwnedContent,
    tree: NestedTree,
    tmp_path: Path,
) -> None:
    buried = _stored(tmp_path, tree.buried_file_id)

    assert _delete_folder(client, owned.folder_id, tmp_path) == 200
    assert not buried.exists()


def test_a_file_outside_the_deleted_subtree_stays_in_storage(
    client: TestClient,
    owned: OwnedContent,
    tree: NestedTree,
    tmp_path: Path,
) -> None:
    outside = _stored(tmp_path, tree.sibling_file_id)

    assert _delete_folder(client, owned.folder_id, tmp_path) == 200
    assert outside.exists()


def test_a_folder_outside_the_deleted_subtree_survives(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    tree: NestedTree,
    tmp_path: Path,
) -> None:
    assert _delete_folder(client, owned.folder_id, tmp_path) == 200
    assert surviving_folder_ids(sessions) == {
        owned.home_id,
        tree.sibling_folder_id,
    }
    assert surviving_ids(sessions, File) == {tree.sibling_file_id}
