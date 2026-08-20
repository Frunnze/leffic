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
from tests.support import authorization, in_memory_sessions

_NOT_FOUND = 404


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


def test_a_note_id_is_never_a_deck_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-deck/", "deck_id", owned.note_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT
    assert surviving_ids(sessions, Note) == {owned.note_id}


def test_a_folder_id_is_never_a_deck_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-deck/", "deck_id", owned.folder_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT
    assert owned.folder_id in surviving_folder_ids(sessions)


def test_a_deck_id_is_never_a_file_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-file/", "file_id", owned.deck_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FILE
    assert surviving_ids(sessions, FlashcardDeck) == {owned.deck_id}


def test_a_file_id_is_never_a_note_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-note/", "note_id", owned.file_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT
    assert surviving_ids(sessions, File) == {owned.file_id}


def test_a_test_id_is_never_a_folder_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client,
        "/delete-folder/",
        "folder_id",
        owned.test_id,
        authorization(),
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_FOLDER
    assert surviving_ids(sessions, Test) == {owned.test_id}


def test_a_deck_id_is_never_a_test_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-test/", "test_id", owned.deck_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT
    assert surviving_ids(sessions, FlashcardDeck) == {owned.deck_id}


def test_a_home_folder_id_is_never_a_note_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-note/", "note_id", owned.home_id, authorization()
    )

    assert code == _NOT_FOUND
    assert body["detail"] == MISSING_UNIT
    assert owned.home_id in surviving_folder_ids(sessions)
