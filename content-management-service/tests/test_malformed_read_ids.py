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
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.support import authorization, in_memory_sessions

_READ_ENDPOINTS = (
    ("/note", "note_id"),
    ("/flashcards", "flashcard_deck_id"),
    ("/test-items", "test_id"),
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
def test_a_hostile_note_id_reads_as_a_missing_note(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.note_id

    code, body = read_unit(
        client, "/note", "note_id", unit_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_NOTE


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_deck_id_reads_as_a_missing_deck(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.deck_id

    code, body = read_unit(
        client,
        "/flashcards",
        "flashcard_deck_id",
        unit_id,
        authorization(),
    )

    assert code == 404
    assert body["detail"] == MISSING_DECK


@pytest.mark.parametrize("unit_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_test_id_reads_as_a_missing_test(
    client: TestClient, owned: OwnedContent, unit_id: str
) -> None:
    assert owned.test_id

    code, body = read_unit(
        client, "/test-items", "test_id", unit_id, authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_TEST


@pytest.mark.parametrize(("path", "parameter"), _READ_ENDPOINTS)
def test_an_empty_id_is_never_a_server_error(
    client: TestClient, owned: OwnedContent, path: str, parameter: str
) -> None:
    assert owned.note_id

    code, _body = read_unit(client, path, parameter, "", authorization())

    assert code == 404


def test_no_hostile_test_id_opens_a_session(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    assert owned.test_id

    for unit_id in HOSTILE_IDENTIFIERS:
        code, _body = read_unit(
            client, "/test-items", "test_id", unit_id, authorization()
        )

        assert code == 404

    assert opened_test_sessions(sessions) == 0


def test_an_empty_test_id_opens_no_session(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    assert owned.test_id

    code, _body = read_unit(
        client, "/test-items", "test_id", "", authorization()
    )

    assert code == 404
    assert opened_test_sessions(sessions) == 0
