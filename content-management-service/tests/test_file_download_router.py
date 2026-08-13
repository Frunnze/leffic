import subprocess
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.file_upload import file_uploader as upload_module

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"


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


def test_downloading_a_missing_file_is_not_found(client: TestClient) -> None:
    response = client.get(
        "/file", params={"file_id": "x", "file_extension": "pdf"}
    )

    assert response.status_code == 404


def test_downloading_a_pdf_returns_it_directly(
    client: TestClient, tmp_path: Path
) -> None:
    _ = (tmp_path / "doc.pdf").write_bytes(b"%PDF-1.4")

    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.get(
            "/file", params={"file_id": "doc", "file_extension": "pdf"}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_downloading_another_format_converts_it(
    client: TestClient, tmp_path: Path
) -> None:
    _ = (tmp_path / "doc.docx").write_bytes(b"docx bytes")
    libreoffice = WritingLibreOffice(b"%PDF-converted")

    with (
        mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(subprocess, "run", libreoffice),
    ):
        response = client.get(
            "/file", params={"file_id": "doc", "file_extension": "docx"}
        )

    command = libreoffice.commands[0]

    assert response.status_code == 200
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
