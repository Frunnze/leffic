import subprocess
import uuid
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.file_upload import file_uploader as upload_module
from shared.database import get_db
from shared.models import File, Folder
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_NOT_FOUND = 404
_OK = 200
_UNAUTHORIZED = 401

_HOME_ID = uuid.UUID(USER_ID)
_STRANGER_ID = uuid.UUID(OTHER_USER_ID)
_PDF_FILE_ID = "6f1c7d4e-0000-4000-8000-0000000000b1"
_DOCX_FILE_ID = "6f1c7d4e-0000-4000-8000-0000000000b2"
_STRANGER_FILE_ID = "6f1c7d4e-0000-4000-8000-0000000000b3"


class WritingLibreOffice:
    def __init__(self, produced: bytes) -> None:
        self.produced: bytes = produced
        self.commands: list[list[str]] = []
        self.arguments: list[dict[str, object]] = []

    def __call__(
        self, command: list[str], **keyword_arguments: object
    ) -> subprocess.CompletedProcess[bytes]:
        self.commands.append(command)
        self.arguments.append(keyword_arguments)
        output_directory = Path(command[command.index("--outdir") + 1])
        written = output_directory / f"{Path(command[-1]).stem}.pdf"
        _ = written.write_bytes(self.produced)

        return subprocess.CompletedProcess(
            args=command, returncode=0, stderr=b""
        )


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add_all(
            [
                Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID),
                Folder(
                    id=_STRANGER_ID, name="Home", user_id=_STRANGER_ID
                ),
                File(
                    id=uuid.UUID(_PDF_FILE_ID),
                    folder_id=_HOME_ID,
                    name="doc.pdf",
                    extension="pdf",
                ),
                File(
                    id=uuid.UUID(_DOCX_FILE_ID),
                    folder_id=_HOME_ID,
                    name="doc.docx",
                    extension="docx",
                ),
                File(
                    id=uuid.UUID(_STRANGER_FILE_ID),
                    folder_id=_STRANGER_ID,
                    name="secret.pdf",
                    extension="pdf",
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


def test_downloading_a_missing_file_is_not_found(client: TestClient) -> None:
    response = client.get(
        "/file",
        params={"file_id": "x", "file_extension": "pdf"},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


def test_downloading_a_file_needs_a_token(client: TestClient) -> None:
    response = client.get(
        "/file", params={"file_id": _PDF_FILE_ID, "file_extension": "pdf"}
    )

    assert response.status_code == _UNAUTHORIZED


def test_a_strangers_file_cannot_be_downloaded(
    client: TestClient, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{_STRANGER_FILE_ID}.pdf").write_bytes(b"%PDF-1.4")

    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.get(
            "/file",
            params={
                "file_id": _STRANGER_FILE_ID,
                "file_extension": "pdf",
            },
            headers=authorization(),
        )

    assert response.status_code == _NOT_FOUND


def test_downloading_a_pdf_returns_it_directly(
    client: TestClient, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{_PDF_FILE_ID}.pdf").write_bytes(b"%PDF-1.4")

    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.get(
            "/file",
            params={"file_id": _PDF_FILE_ID, "file_extension": "pdf"},
            headers=authorization(),
        )

    assert response.status_code == _OK
    assert response.headers["content-type"] == "application/pdf"


def test_downloading_another_format_converts_it(
    client: TestClient, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{_DOCX_FILE_ID}.docx").write_bytes(b"docx bytes")
    libreoffice = WritingLibreOffice(b"%PDF-converted")

    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(subprocess, "run", libreoffice),
    ):
        response = client.get(
            "/file",
            params={
                "file_id": _DOCX_FILE_ID,
                "file_extension": "docx",
            },
            headers=authorization(),
        )

    command = libreoffice.commands[0]

    assert response.status_code == _OK
    assert response.content == b"%PDF-converted"
    assert command[:4] == [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
    ]
    assert command[4] == "--outdir"
    assert Path(command[6]).suffix == ".docx"
    assert libreoffice.arguments[0] == {
        "capture_output": True,
        "check": False,
        "timeout": 120,
    }
