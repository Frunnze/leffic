import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import cast
from unittest import mock

import textract
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import text_sources
from shared.file_storage import storage_name
from tests.property_support import seeded_file

MISSING_DOCUMENT = "That document is no longer stored"
NO_TEXT = "Could not extract text!"
TOPIC_IS_WRITTEN = "A topic is written into a note, not extracted."
DOCUMENT_BYTES = b"Resting potential is near -70 mV."
DOCUMENT_TEXT = "Resting potential is near -70 mV.\n"
OK = 200
BAD_REQUEST = 400
NOT_FOUND = 404
STORED_EXTENSION = "pdf"


def read_the_document(filename: str, **_: object) -> bytes:
    return Path(filename).read_bytes()


def recorded_file_id(
    sessions: sessionmaker[Session], owner: str
) -> str:
    with sessions() as session:
        return str(seeded_file(session, uuid.UUID(owner)))


def stored_file_id(
    sessions: sessionmaker[Session], owner: str, directory: Path
) -> str:
    file_id = recorded_file_id(sessions, owner)
    stored = directory / storage_name(file_id, STORED_EXTENSION)
    _ = stored.write_bytes(DOCUMENT_BYTES)

    return file_id


@contextmanager
def extraction_world(directory: Path) -> Generator[None]:
    with (
        mock.patch.object(
            text_sources, "_FILES_DIRECTORY", str(directory)
        ),
        mock.patch.object(textract, "process", read_the_document),
    ):
        yield


@contextmanager
def unreadable_storage() -> Generator[mock.Mock]:
    reader = mock.Mock(side_effect=AssertionError("storage was read"))

    with mock.patch.object(text_sources, "get_file_from_storage", reader):
        yield reader


def extract(
    client: TestClient,
    payload: dict[str, object],
    headers: dict[str, str],
) -> tuple[int, dict[str, object]]:
    response = client.post("/extract-text", json=payload, headers=headers)

    return response.status_code, cast(
        "dict[str, object]", response.json()
    )


def file_entries(*file_ids: str) -> dict[str, object]:
    return {
        "file_metadata": [{"file_id": file_id} for file_id in file_ids]
    }
