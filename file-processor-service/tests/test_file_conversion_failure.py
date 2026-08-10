import io
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import jwt
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from app_factory import create_app
from features.file_upload import file_uploader as upload_module

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"


class FakeTaskResult:
    def __init__(self, task_id: str) -> None:
        super().__init__()
        self.id: str = task_id


class FakeTask:
    def __init__(self, task_id: str) -> None:
        super().__init__()
        self.task_id: str = task_id
        self.calls: list[dict[str, object]] = []

    def delay(self, **kwargs: object) -> FakeTaskResult:
        self.calls.append(kwargs)

        return FakeTaskResult(self.task_id)


class FakeAsyncResult:
    def __init__(
        self, status: str, result: dict[str, object] | None
    ) -> None:
        super().__init__()
        self.status: str = status
        self.result: dict[str, object] | None = result

    def ready(self) -> bool:
        return self.result is not None


class FakeAi:
    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        return f"answered {len(history)} messages for {len(system_prompt)}"


class FakeFactory:
    def __init__(self) -> None:
        super().__init__()
        self.models: list[str | None] = []

    def get_ai(self, model: str | None = None) -> FakeAi:
        self.models.append(model)

        return FakeAi()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def _authorization() -> dict[str, str]:
    token = jwt.encode({"user_id": _USER_ID}, "secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


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
        mock.patch.object(upload_module, "register_files"),
    ):
        response = client.post(
            "/upload-files",
            files={"files": ("plainname", b"payload", "text/plain")},
            data={"folder_id": _FOLDER_ID},
            headers=_authorization(),
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
        mock.patch.object(upload_module, "register_files"),
    ):
        response = client.post(
            "/upload-files",
            files={"files": ("sheet.Xml", b"payload", "text/xml")},
            data={"folder_id": _FOLDER_ID},
            headers=_authorization(),
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
