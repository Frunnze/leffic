import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
import requests
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import Flashcard, FlashcardDeck, Folder
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)


class FakeResponse:
    def __init__(
        self, payload: dict[str, object], status_code: int = 200
    ) -> None:
        super().__init__()
        self.payload: dict[str, object] = payload
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self) -> dict[str, object]:
        return self.payload


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def deck_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
        session.add(folder)
        deck = FlashcardDeck(folder_id=folder.id, name="Deck")
        deck.flashcards.append(Flashcard(type="basic", content={"q": "a"}))
        session.add(deck)
        session.commit()

        return str(deck.id)


def test_a_card_due_tomorrow_is_not_offered(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        session.query(Flashcard).one().next_review = datetime.now(
            UTC
        ) + timedelta(days=1)
        session.commit()

    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": deck_id},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 0


def test_a_card_due_today_is_offered(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        session.query(Flashcard).one().next_review = datetime.now(UTC)
        session.commit()

    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": deck_id},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 1


def test_a_card_in_another_deck_is_not_offered(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        other = FlashcardDeck(folder_id=_HOME_ID, name="Other")
        other.flashcards.append(Flashcard(type="basic", content={"q": "b"}))
        session.add(other)
        session.commit()
        other_id = str(other.id)

    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": other_id},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 1


def test_another_users_cards_are_not_offered(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        stranger = uuid.UUID(OTHER_USER_ID)
        session.add(
            Folder(id=stranger, name="Home", user_id=stranger)
        )
        deck = FlashcardDeck(folder_id=stranger, name="Theirs")
        deck.flashcards.append(Flashcard(type="basic", content={"q": "c"}))
        session.add(deck)
        session.commit()

    response = client.get(
        "/flashcards",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 1


def test_a_due_card_is_described_in_full(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id
    made_at = datetime(2026, 8, 8, 17, 0, 0)  # noqa: DTZ001

    with sessions() as session:
        card = session.query(Flashcard).one()
        card.created_at = made_at
        card.fsrs_card = {"stability": 1.0}
        session.commit()
        card_id = card.id

    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": deck_id},
        headers=authorization(),
    )
    body = cast("dict[str, list[dict[str, object]]]", response.json())

    assert body["flashcards"] == [
        {
            "id": card_id,
            "type": "basic",
            "next_review": None,
            "content": {"q": "a"},
            "created_at": "2026-08-08 17:00:00",
            "fsrs_card": {"stability": 1.0},
        }
    ]


def test_a_reviewed_card_reports_its_next_review(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id
    due_at = datetime(2026, 8, 8, 9, 30, 0)  # noqa: DTZ001

    with sessions() as session:
        session.query(Flashcard).one().next_review = due_at
        session.commit()

    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": deck_id},
        headers=authorization(),
    )
    body = cast("dict[str, list[dict[str, object]]]", response.json())

    assert body["flashcards"][0]["next_review"] == "2026-08-08 09:30:00"
