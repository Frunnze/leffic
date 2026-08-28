from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import MISSING_FILE, scoped_client
from tests.extraction_support import (
    BAD_REQUEST,
    DOCUMENT_TEXT,
    MISSING_DOCUMENT,
    NOT_FOUND,
    OK,
    extract,
    extraction_world,
    file_entries,
    recorded_file_id,
    stored_file_id,
    unreadable_storage,
)
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    authorization,
    in_memory_sessions,
)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_the_owner_extracts_text(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)

    with extraction_world(tmp_path):
        code, body = extract(
            client, file_entries(file_id), authorization(USER_ID)
        )

    assert code == OK
    assert body == {"text": DOCUMENT_TEXT}


def test_the_stored_extension_is_used(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)
    payload: dict[str, object] = {
        "file_metadata": [{"file_id": file_id, "extension": "xyz"}]
    }

    with extraction_world(tmp_path):
        code, body = extract(client, payload, authorization(USER_ID))

    assert code == OK
    assert body == {"text": DOCUMENT_TEXT}


def test_a_strangers_file_is_404(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, OTHER_USER_ID, tmp_path)

    with extraction_world(tmp_path):
        code, body = extract(
            client, file_entries(file_id), authorization(USER_ID)
        )

    assert code == NOT_FOUND
    assert body == {"detail": MISSING_FILE}


@pytest.mark.parametrize("hostile", HOSTILE_IDENTIFIERS)
def test_hostile_identifiers_are_404_and_read_nothing(
    client: TestClient, hostile: str
) -> None:
    with unreadable_storage() as reader:
        code, body = extract(
            client, file_entries(hostile), authorization(USER_ID)
        )

    assert code == NOT_FOUND
    assert body == {"detail": MISSING_FILE}
    assert reader.call_count == 0


def test_one_foreign_id_aborts_the_whole_request(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    owned = stored_file_id(sessions, USER_ID, tmp_path)
    foreign = stored_file_id(sessions, OTHER_USER_ID, tmp_path)

    with unreadable_storage() as reader:
        code, body = extract(
            client, file_entries(owned, foreign), authorization(USER_ID)
        )

    assert code == NOT_FOUND
    assert body == {"detail": MISSING_FILE}
    assert reader.call_count == 0


def test_a_repeated_id_is_extracted_once_per_entry(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)

    with extraction_world(tmp_path):
        code, body = extract(
            client, file_entries(file_id, file_id), authorization(USER_ID)
        )

    assert code == OK
    assert body == {"text": DOCUMENT_TEXT * 2}


def test_owned_but_unstored_document_is_400(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = recorded_file_id(sessions, USER_ID)

    with extraction_world(tmp_path):
        code, body = extract(
            client, file_entries(file_id), authorization(USER_ID)
        )

    assert code == BAD_REQUEST
    assert body == {"msg": MISSING_DOCUMENT}
