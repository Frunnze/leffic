from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import File, FlashcardDeck, Note, Test
from tests.access_support import (
    HOME_ID,
    MISSING_FILE,
    MISSING_FOLDER,
    MISSING_UNIT,
    OwnedContent,
    crashless_client,
    delete_unit,
    seeded_content,
    surviving_folder_ids,
    surviving_ids,
)
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.support import authorization, in_memory_sessions

_NOT_FOUND = 404

_DELETE_ENDPOINTS = (
    ("/delete-deck/", "deck_id"),
    ("/delete-test/", "test_id"),
    ("/delete-note/", "note_id"),
    ("/delete-file/", "file_id"),
    ("/delete-folder/", "folder_id"),
)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_deck_id_reads_as_a_missing_unit(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.deck_id

    code, body = delete_unit(
        client, "/delete-deck/", "deck_id", unit_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_test_id_reads_as_a_missing_unit(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.test_id

    code, body = delete_unit(
        client, "/delete-test/", "test_id", unit_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_note_id_reads_as_a_missing_unit(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.note_id

    code, body = delete_unit(
        client, "/delete-note/", "note_id", unit_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_file_id_reads_as_a_missing_file(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.file_id

    code, body = delete_unit(
        client, "/delete-file/", "file_id", unit_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FILE


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_folder_id_reads_as_a_missing_folder(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.folder_id

    code, body = delete_unit(
        client, "/delete-folder/", "folder_id", unit_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FOLDER


@pytest.mark.parametrize(("path", "parameter"), _DELETE_ENDPOINTS)
def test_an_empty_id_is_never_a_server_error(
    client: TestClient, owned: OwnedContent, path: str, parameter: str
) -> None:
    assert owned.folder_id

    code, _body = delete_unit(client, path, parameter, "", authorization())

    assert code == _NOT_FOUND


def test_no_hostile_id_deletes_anything(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    for path, parameter in _DELETE_ENDPOINTS:
        for unit_id in HOSTILE_IDENTIFIERS:
            code, _body = delete_unit(
                client, path, parameter, unit_id, authorization()
            )

            assert code == _NOT_FOUND

    assert surviving_ids(sessions, FlashcardDeck) == {owned.deck_id}
    assert surviving_ids(sessions, Test) == {owned.test_id}
    assert surviving_ids(sessions, Note) == {owned.note_id}
    assert surviving_ids(sessions, File) == {owned.file_id}
    assert surviving_folder_ids(sessions) == {
        owned.home_id,
        owned.folder_id,
    }
