import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import jwt
import pytest
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


def test_uploading_stores_each_file_and_registers_the_names(
    client: TestClient, tmp_path: Path
) -> None:
    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(upload_module, "register_files") as save,
    ):
        response = client.post(
            "/upload-files",
            files={"files": ("notes.pdf", b"payload", "application/pdf")},
            data={"folder_id": _FOLDER_ID},
            headers=_authorization(),
        )

    body = cast("dict[str, object]", response.json())
    metadata = cast("list[dict[str, str]]", body["file_metadata"])
    stored = metadata[0]

    assert body["msg"] == "Files uploaded!"
    assert stored["extension"] == "pdf"
    assert stored["name"] == "notes.pdf"
    assert uuid.UUID(stored["file_id"]).version == 4
    assert save.call_args.args[0] == [stored]
    assert save.call_args.args[1] == _FOLDER_ID
    assert (tmp_path / f"{stored['file_id']}.pdf").read_bytes() == b"payload"


def test_uploading_to_home_uses_the_caller_folder(
    client: TestClient, tmp_path: Path
) -> None:
    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(upload_module, "register_files") as save,
    ):
        _ = client.post(
            "/upload-files",
            files={"files": ("notes.pdf", b"payload", "application/pdf")},
            data={"folder_id": "home"},
            headers=_authorization(),
        )

    assert save.call_args.args[1] == _USER_ID
