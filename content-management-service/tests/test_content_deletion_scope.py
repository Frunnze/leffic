from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import FlashcardDeck, Note, Test
from tests.access_support import (
    HOME_ID,
    MISSING_UNIT,
    OTHER_HOME_ID,
    OwnedContent,
    delete_unit,
    scoped_client,
    seeded_content,
    surviving_ids,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def intruder(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


def test_another_users_deck_cannot_be_deleted(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = delete_unit(
        client, "/delete-deck/", "deck_id", owned.deck_id, intruder
    )

    assert code == 404
    assert body["detail"] == MISSING_UNIT
    assert owned.deck_id in surviving_ids(sessions, FlashcardDeck)


def test_another_users_test_cannot_be_deleted(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = delete_unit(
        client, "/delete-test/", "test_id", owned.test_id, intruder
    )

    assert code == 404
    assert body["detail"] == MISSING_UNIT
    assert owned.test_id in surviving_ids(sessions, Test)


def test_another_users_note_cannot_be_deleted(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    code, body = delete_unit(
        client, "/delete-note/", "note_id", owned.note_id, intruder
    )

    assert code == 404
    assert body["detail"] == MISSING_UNIT
    assert owned.note_id in surviving_ids(sessions, Note)


def test_deleting_a_deck_without_a_token_is_refused(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, _body = delete_unit(
        client, "/delete-deck/", "deck_id", owned.deck_id, {}
    )

    assert code == 401
    assert owned.deck_id in surviving_ids(sessions, FlashcardDeck)


def test_deleting_a_test_without_a_token_is_refused(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, _body = delete_unit(
        client, "/delete-test/", "test_id", owned.test_id, {}
    )

    assert code == 401
    assert owned.test_id in surviving_ids(sessions, Test)


def test_deleting_a_note_without_a_token_is_refused(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, _body = delete_unit(
        client, "/delete-note/", "note_id", owned.note_id, {}
    )

    assert code == 401
    assert owned.note_id in surviving_ids(sessions, Note)


def test_an_owner_still_deletes_their_own_deck(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-deck/", "deck_id", owned.deck_id, authorization()
    )

    assert code == 200
    assert body == {"msg": "Deck deleted!"}
    assert surviving_ids(sessions, FlashcardDeck) == set()


def test_an_owner_still_deletes_their_own_test(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-test/", "test_id", owned.test_id, authorization()
    )

    assert code == 200
    assert body == {"msg": "Test deleted!"}
    assert surviving_ids(sessions, Test) == set()


def test_an_owner_still_deletes_their_own_note(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    code, body = delete_unit(
        client, "/delete-note/", "note_id", owned.note_id, authorization()
    )

    assert code == 200
    assert body == {"msg": "Note deleted!"}
    assert surviving_ids(sessions, Note) == set()
