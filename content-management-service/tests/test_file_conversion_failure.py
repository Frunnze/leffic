import io
import subprocess
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.file_upload import file_uploader as upload_module
from shared.database import get_db
from shared.models import Folder
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


def test_a_failed_conversion_is_reported(
    client: TestClient, tmp_path: Path
) -> None:
    _ = (tmp_path / "doc.docx").write_bytes(b"docx bytes")
    failed = subprocess.CompletedProcess(
        args=[], returncode=1, stderr=b"libreoffice exploded"
    )

    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(subprocess, "run", return_value=failed),
    ):
        response = client.get(
            "/file", params={"file_id": "doc", "file_extension": "docx"}
        )

    assert response.status_code == 400
    assert "libreoffice exploded" in response.json()["detail"]


def test_a_file_without_an_extension_keeps_an_empty_one(
    client: TestClient, tmp_path: Path
) -> None:
    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
    ):
        response = client.post(
            "/upload-files",
            files={"files": ("plainname", b"payload", "text/plain")},
            data={"folder_id": _FOLDER_ID},
            headers=authorization(),
        )

    body = cast("dict[str, object]", response.json())
    stored = cast("list[dict[str, str]]", body["file_metadata"])[0]

    assert stored["extension"] == ""
    assert stored["name"] == "plainname"


def test_an_extension_starting_with_a_letter_keeps_it(
    client: TestClient, tmp_path: Path
) -> None:
    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
    ):
        response = client.post(
            "/upload-files",
            files={"files": ("sheet.Xml", b"payload", "text/xml")},
            data={"folder_id": _FOLDER_ID},
            headers=authorization(),
        )

    body = cast("dict[str, object]", response.json())
    stored = cast("list[dict[str, str]]", body["file_metadata"])[0]

    assert stored["extension"] == "Xml"
    assert stored["name"] == "sheet.Xml"


def test_a_file_without_a_filename_is_stored_without_one(
    tmp_path: Path,
) -> None:
    upload = UploadFile(file=io.BytesIO(b"payload"), filename=None)

    with mock.patch.object(
        upload_module, "_FILES_DIRECTORY", str(tmp_path)
    ):
        stored = upload_module._stored_file(upload)

    assert stored["name"] == ""
    assert stored["extension"] == ""
