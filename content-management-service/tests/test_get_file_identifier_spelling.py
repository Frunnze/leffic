"""
Bug hunt: GET /file's ownership/id handling across equivalent UUID
spellings (uppercase, braces, urn:, bare hex). Oracle: differential --
every textual spelling of the SAME uuid must produce the SAME outcome,
matching the codebase's own established contract already proven for
/note and /flashcards in
tests/test_identifier_spelling_scope.py::test_every_spelling_of_an_owned_id_reads_alike.

Concrete inputs -> expected outputs:
- input: a stranger requests GET /file with every spelling of
  owned.file_id (e.g. "8230C144-...B7", "{8230c144-...-b7}",
  "urn:uuid:8230c144-...-b7", "8230c144...b7") and file_extension="pdf"
  output: every spelling -> 404, {"detail": "File does not exist!"}
- input: the owner requests GET /file with every spelling of their own
  file_id, file_extension="pdf", and the real bytes stored on disk as
  "<canonical-lowercase-uuid>.pdf"
  output: every spelling -> 200 with the identical stored bytes
  (currently the non-canonical spellings wrongly 404, because the raw
  query text -- not the canonical id the ownership check already
  resolved -- is used to build the file path).
"""

from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.file_upload import file_uploader as upload_module
from tests.access_support import (
    HOME_ID,
    MISSING_FILE,
    OwnedContent,
    identifier_spellings,
    scoped_client,
    seeded_content,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions

_OK = 200
_NOT_FOUND = 404
_PDF_BYTES = b"%PDF-1.4 test bytes"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


def test_no_spelling_of_a_foreign_file_id_is_ever_downloaded(
    client: TestClient, owned: OwnedContent
) -> None:
    intruder = authorization(OTHER_USER_ID)

    for spelling in identifier_spellings(owned.file_id):
        response = client.get(
            "/file",
            params={"file_id": spelling, "file_extension": "pdf"},
            headers=intruder,
        )

        assert response.status_code == _NOT_FOUND
        assert response.json() == {"detail": MISSING_FILE}


def test_every_spelling_of_an_owned_file_id_downloads_the_same_bytes(
    client: TestClient, owned: OwnedContent, tmp_path: Path
) -> None:
    _ = (tmp_path / f"{owned.file_id}.pdf").write_bytes(_PDF_BYTES)

    with mock.patch.object(upload_module, "_FILES_DIRECTORY", str(tmp_path)):
        answers = [
            client.get(
                "/file",
                params={"file_id": spelling, "file_extension": "pdf"},
                headers=authorization(),
            )
            for spelling in identifier_spellings(owned.file_id)
        ]

    statuses = [answer.status_code for answer in answers]
    bodies = [answer.content for answer in answers]

    assert statuses == [_OK] * len(answers)
    assert bodies == [_PDF_BYTES] * len(answers)
