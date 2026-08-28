import io
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import cast
from unittest import mock

from fastapi import UploadFile
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import strategies as st
from sqlalchemy.orm import Session, sessionmaker

from features.file_upload import file_uploader as uploader_module
from shared import file_storage
from shared.file_storage import storage_name
from shared.models import Folder
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions

LEARNER_FOLDER_ID = "6f1c7d4e-0000-4000-8000-00000000000a"
FOREIGN_FOLDER_ID = "6f1c7d4e-0000-4000-8000-00000000000b"
UNKNOWN_FOLDER_ID = "6f1c7d4e-0000-4000-8000-00000000000c"
NOT_FOUND = 404
OK = 200
SERVER_ERROR = 500
DEFAULT_UPLOAD_NAMES = ("notes.pdf",)
EXTENSIONS = st.sampled_from(["pdf", "docx", "txt", "png"])
STORAGE_FAILURE_MESSAGE = "storage is on fire"
RECORDED_FILES = "features.file_upload.file_uploader._recorded_files"


def sessions_without_a_home_folder() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add_all(
            [
                Folder(
                    id=uuid.UUID(LEARNER_FOLDER_ID),
                    name="Biology",
                    user_id=uuid.UUID(USER_ID),
                ),
                Folder(
                    id=uuid.UUID(FOREIGN_FOLDER_ID),
                    name="Chemistry",
                    user_id=uuid.UUID(OTHER_USER_ID),
                ),
            ]
        )
        session.commit()

    return factory


@contextmanager
def storage_directory(directory: Path) -> Generator[Path]:
    with mock.patch.object(
        uploader_module, "_FILES_DIRECTORY", str(directory)
    ), mock.patch.object(
        file_storage, "_FILES_DIRECTORY", str(directory)
    ):
        yield directory


def upload(
    client: TestClient,
    folder_id: str | None,
    headers: dict[str, str],
    filenames: tuple[str, ...] = DEFAULT_UPLOAD_NAMES,
) -> Response:
    sent = [
        ("files", (name, b"payload", "application/pdf"))
        for name in filenames
    ]
    form = {} if folder_id is None else {"folder_id": folder_id}

    return client.post(
        "/upload-files", files=sent, data=form, headers=headers
    )


def refusal_detail(response: Response) -> str:
    body = cast("dict[str, str]", response.json())

    return body["detail"]


def uploaded_metadata(response: Response) -> list[dict[str, str]]:
    body = cast("dict[str, object]", response.json())

    return cast("list[dict[str, str]]", body["file_metadata"])


def names_in(directory: Path) -> set[str]:
    return {stored.name for stored in directory.iterdir()}


def an_upload(filename: str, content: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(content))


def numbered_filenames(count: int, extension: str) -> tuple[str, ...]:
    return tuple(
        f"notes-{index}.{extension}" for index in range(count)
    )


def stored_uploads(
    directory: Path, filenames: tuple[str, ...]
) -> list[dict[str, str]]:
    written: list[dict[str, str]] = []

    with storage_directory(directory):
        for filename in filenames:
            file = an_upload(filename, b"payload")
            metadata = uploader_module._uploaded_file_metadata(file)
            uploader_module.save_file_to_storage(
                file,
                storage_name(
                    metadata["file_id"], metadata["extension"]
                ),
            )
            written.append(metadata)

    return written


def emptied(directory: Path) -> Path:
    for stored in directory.iterdir():
        stored.unlink()

    return directory


class FailingStorageWriter:
    def __init__(self, failing_index: int) -> None:
        self.failing_index: int = failing_index
        self.calls: int = 0

    def __call__(self, file: UploadFile, unique_name: str) -> None:
        current_call = self.calls
        self.calls += 1

        if current_call == self.failing_index:
            raise RuntimeError(STORAGE_FAILURE_MESSAGE)

        uploader_module.save_file_to_storage(file, unique_name)
