from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.file_upload import file_uploader as uploader_module
from shared.file_storage import storage_name
from tests.access_support import scoped_client
from tests.file_upload_support import (
    LEARNER_FOLDER_ID,
    names_in,
    sessions_without_a_home_folder,
    storage_directory,
    upload,
    uploaded_metadata,
)
from tests.support import USER_ID, authorization

_OK = 200


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return sessions_without_a_home_folder()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_uploader_defines_no_private_storage_name() -> None:
    assert not hasattr(uploader_module, "_storage_name")


def test_an_upload_is_written_under_the_shared_storage_name(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(
            client, LEARNER_FOLDER_ID, authorization(USER_ID), ("notes.pdf",)
        )

    described = uploaded_metadata(response)[0]

    assert response.status_code == _OK
    assert names_in(tmp_path) == {
        storage_name(described["file_id"], described["extension"])
    }


def test_an_extensionless_upload_is_written_under_its_bare_id(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(
            client, LEARNER_FOLDER_ID, authorization(USER_ID), ("archive",)
        )

    described = uploaded_metadata(response)[0]

    assert names_in(tmp_path) == {described["file_id"]}


def test_cleanup_unlinks_the_shared_storage_name(tmp_path: Path) -> None:
    described = {
        "file_id": "6f1c7d4e-0000-4000-8000-00000000000d",
        "extension": "pdf",
        "name": "notes.pdf",
    }
    stored = tmp_path / storage_name(
        described["file_id"], described["extension"]
    )
    _ = stored.write_bytes(b"payload")

    with storage_directory(tmp_path):
        uploader_module._remove_uploaded_files_from_storage([described])

    assert not stored.exists()
