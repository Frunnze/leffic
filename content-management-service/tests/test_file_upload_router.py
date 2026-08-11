import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.file_upload import file_uploader as upload_module
from shared.database import get_db
from shared.models import File, Folder
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

HOME_ID = uuid.UUID(USER_ID)
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add_all(
            [
                Folder(id=HOME_ID, name="Home", user_id=HOME_ID),
                Folder(
                    id=uuid.UUID(_FOLDER_ID),
                    parent_id=HOME_ID,
                    name="Biology",
                    user_id=HOME_ID,
                ),
            ]
        )
        session.commit()

    return factory


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def _upload(
    client: TestClient, folder_id: str, storage: Path
) -> dict[str, str]:
    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(storage)):
        response = client.post(
            "/upload-files",
            files={"files": ("notes.pdf", b"payload", "application/pdf")},
            data={"folder_id": folder_id},
            headers=authorization(),
        )

    body = cast("dict[str, object]", response.json())
    metadata = cast("list[dict[str, str]]", body["file_metadata"])

    return metadata[0]


def test_uploading_stores_the_bytes_and_records_the_file(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    stored = _upload(client, _FOLDER_ID, tmp_path)

    assert stored["extension"] == "pdf"
    assert stored["name"] == "notes.pdf"
    assert uuid.UUID(stored["file_id"]).version == 4
    assert (tmp_path / f"{stored['file_id']}.pdf").read_bytes() == b"payload"

    with sessions() as session:
        recorded = session.query(File).one()

        assert str(recorded.id) == stored["file_id"]
        assert recorded.name == "notes.pdf"
        assert str(recorded.folder_id) == _FOLDER_ID


def test_uploading_to_home_uses_the_caller_folder(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    _ = _upload(client, "home", tmp_path)

    with sessions() as session:
        recorded = session.query(File).one()

        assert str(recorded.folder_id) == USER_ID


def test_uploading_into_a_missing_folder_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.post(
            "/upload-files",
            files={"files": ("notes.pdf", b"payload", "application/pdf")},
            data={"folder_id": str(uuid.uuid4())},
            headers=authorization(),
        )

    body = cast("dict[str, str]", response.json())

    assert response.status_code == 404
    assert body["detail"] == "Folder does not exist!"


def test_uploading_needs_a_token(client: TestClient, tmp_path: Path) -> None:
    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.post(
            "/upload-files",
            files={"files": ("notes.pdf", b"payload", "application/pdf")},
            data={"folder_id": "home"},
        )

    assert response.status_code == 401


def test_uploading_without_a_folder_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.post(
            "/upload-files",
            files={"files": ("notes.pdf", b"payload", "application/pdf")},
            headers=authorization(),
        )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == 404
    assert body["detail"] == "Folder does not exist!"
