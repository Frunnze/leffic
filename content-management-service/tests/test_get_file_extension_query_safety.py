"""
Bug hunt: GET /file's file_extension query parameter is never checked
against the file's DB-stored extension and is concatenated straight
into the on-disk path. Oracle: implicit (no crash, no bytes leaked
outside _FILES_DIRECTORY) plus exact status.

Concrete inputs -> expected outputs:
- input: an owner's real file_id is stored on disk only as
  "<uuid>.pdf"; the request asks for
  file_extension="../../../../../../etc/passwd"
  output: 404, {"detail": "File not found"}, and no file outside
  _FILES_DIRECTORY is ever opened or returned.
- input: the same owned file_id, requested with file_extension="txt"
  while the real file is stored as "<uuid>.pdf"
  output: 404 (the mismatched extension never falls back to the real
  stored extension).
- input: the same owned file_id and its real "pdf" extension, but with
  a null byte appended: "pdf\\x00x"
  output: 404, not a 500 -- pathlib must not raise on the caller-
  controlled extension text.
"""

from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session, sessionmaker

from features.file_upload import file_uploader as upload_module
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
)
from tests.support import authorization, in_memory_sessions

_NOT_FOUND = 404
_FILE_NOT_FOUND_DETAIL = "File not found"
_PDF_BYTES = b"%PDF-1.4 test bytes"
_SECRET_BYTES = b"root:x:0:0:root:/root:/bin/bash"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


def _requested(
    client: TestClient, tmp_path: Path, file_id: str, file_extension: str
) -> Response:
    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        return client.get(
            "/file",
            params={"file_id": file_id, "file_extension": file_extension},
            headers=authorization(),
        )


def test_a_traversal_extension_neither_crashes_nor_leaks_a_file(
    client: TestClient, owned: OwnedContent, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{owned.file_id}.pdf").write_bytes(_PDF_BYTES)
    outside_secret = tmp_path.parent / "passwd"
    _ = outside_secret.write_bytes(_SECRET_BYTES)

    response = _requested(
        client, tmp_path, owned.file_id, "../../../../../../etc/passwd"
    )

    assert response.status_code == _NOT_FOUND
    assert response.json() == {"detail": _FILE_NOT_FOUND_DETAIL}
    assert _SECRET_BYTES not in response.content


def test_an_extension_that_does_not_match_storage_is_not_found(
    client: TestClient, owned: OwnedContent, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{owned.file_id}.pdf").write_bytes(_PDF_BYTES)

    response = _requested(client, tmp_path, owned.file_id, "txt")

    assert response.status_code == _NOT_FOUND
    assert response.json() == {"detail": _FILE_NOT_FOUND_DETAIL}


def test_a_null_byte_in_the_extension_is_not_found_not_a_crash(
    client: TestClient, owned: OwnedContent, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{owned.file_id}.pdf").write_bytes(_PDF_BYTES)

    response = _requested(client, tmp_path, owned.file_id, "pdf\x00x")

    assert response.status_code == _NOT_FOUND
