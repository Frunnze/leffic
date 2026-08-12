from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    HOME_ID,
    MISSING_DECK,
    MISSING_NOTE,
    MISSING_TEST,
    OwnedContent,
    crashless_client,
    opened_test_sessions,
    read_unit,
    seeded_content,
)
from tests.support import authorization, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


def test_a_folder_id_is_never_a_note_id(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = read_unit(
        client, "/note", "note_id", owned.folder_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_NOTE


def test_a_home_folder_id_is_never_a_note_id(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = read_unit(
        client, "/note", "note_id", owned.home_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_NOTE


def test_a_note_id_is_never_a_deck_id(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = read_unit(
        client,
        "/flashcards",
        "flashcard_deck_id",
        owned.note_id,
        authorization(),
    )

    assert code == 404
    assert body["detail"] == MISSING_DECK


def test_a_folder_id_is_never_a_deck_id(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = read_unit(
        client,
        "/flashcards",
        "flashcard_deck_id",
        owned.folder_id,
        authorization(),
    )

    assert code == 404
    assert body["detail"] == MISSING_DECK


def test_a_deck_id_is_never_a_test_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = read_unit(
        client, "/test-items", "test_id", owned.deck_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_TEST
    assert opened_test_sessions(sessions) == 0


def test_a_file_id_is_never_a_test_id(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = read_unit(
        client, "/test-items", "test_id", owned.file_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_TEST
    assert opened_test_sessions(sessions) == 0


def test_a_test_id_is_never_a_note_id(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = read_unit(
        client, "/note", "note_id", owned.test_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_NOTE
