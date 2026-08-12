import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import FlashcardDeck
from tests.access_support import (
    HOME_ID,
    MISSING_DECK,
    OTHER_HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
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


def _read_deck_cards(
    client: TestClient, deck_id: str, headers: dict[str, str]
) -> tuple[int, dict[str, object]]:
    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": deck_id},
        headers=headers,
    )

    return response.status_code, cast("dict[str, object]", response.json())


def test_another_users_deck_cards_cannot_be_read(
    client: TestClient, owned: OwnedContent, intruder: dict[str, str]
) -> None:
    code, body = _read_deck_cards(client, owned.deck_id, intruder)

    assert code == 404
    assert body["detail"] == MISSING_DECK


def test_another_users_empty_deck_is_not_an_empty_list(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    with sessions() as session:
        cardless = FlashcardDeck(
            folder_id=uuid.UUID(owned.folder_id), name="Empty"
        )
        session.add(cardless)
        session.commit()
        cardless_id = str(cardless.id)

    code, body = _read_deck_cards(client, cardless_id, intruder)

    assert code == 404
    assert "total_flashcards" not in body


def test_reading_deck_cards_without_a_token_is_refused(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = _read_deck_cards(client, owned.deck_id, {})

    assert code == 401
    assert "flashcards" not in body


def test_an_owner_still_reads_their_own_deck_cards(
    client: TestClient, owned: OwnedContent
) -> None:
    code, body = _read_deck_cards(client, owned.deck_id, authorization())
    cards = cast("list[dict[str, object]]", body["flashcards"])

    assert code == 200
    assert body["total_flashcards"] == 1
    assert cards[0]["content"] == {"q": "a"}


def test_a_deck_that_was_never_created_is_reported_as_missing(
    client: TestClient, owned: OwnedContent
) -> None:
    assert owned.deck_id

    code, body = _read_deck_cards(
        client, str(uuid.uuid4()), authorization()
    )

    assert code == 404
    assert body["detail"] == MISSING_DECK


def test_folder_scoped_cards_are_still_listed(
    client: TestClient, owned: OwnedContent
) -> None:
    assert owned.deck_id
    response = client.get(
        "/flashcards", params={"folder_id": "home"}, headers=authorization()
    )
    body = cast("dict[str, object]", response.json())

    assert response.status_code == 200
    assert body["total_flashcards"] == 1
