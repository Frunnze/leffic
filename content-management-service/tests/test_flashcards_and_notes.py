import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import cast
from unittest import mock

import pytest
import requests
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from src.app_factory import create_app
from src.shared.database import get_db
from src.shared.models import Flashcard, FlashcardDeck, Folder
from tests.support import (
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


def test_due_flashcards_from_a_deck(
    client: TestClient, deck_id: str
) -> None:
    response = client.get(
        "/flashcards",
        params={"flashcard_deck_id": deck_id},
        headers=authorization(),
    )

    body = cast("dict[str, object]", response.json())

    assert body["total_flashcards"] == 1


def test_due_flashcards_from_a_folder(
    client: TestClient, deck_id: str
) -> None:
    assert deck_id
    response = client.get(
        "/flashcards",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    body = cast("dict[str, object]", response.json())

    assert body["total_flashcards"] == 1


def test_flashcards_need_a_deck_or_folder(client: TestClient) -> None:
    response = client.get("/flashcards", headers=authorization())

    assert response.status_code == 404


def test_reviewing_a_flashcard_stores_the_schedule(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        card = session.query(Flashcard).one()
        card_id = card.id

    due = (datetime.now(UTC) + timedelta(days=3)).isoformat()
    scheduled: dict[str, object] = {
        "new_card": {"due": due, "card_id": 1},
        "review_log": {"rating": 3},
    }

    with mock.patch.object(
        requests, "post", return_value=FakeResponse(scheduled)
    ):
        response = client.post(
            "/review-flashcard",
            json={"flashcard_id": card_id, "rating": 3},
            headers=authorization(),
        )

    assert response.status_code == 200
    assert cast("dict[str, object]", response.json())["due_date"]


def test_reviewing_an_unknown_flashcard_is_not_found(
    client: TestClient,
) -> None:
    response = client.post(
        "/review-flashcard",
        json={"flashcard_id": 999, "rating": 3},
        headers=authorization(),
    )

    assert response.status_code == 404


def test_a_scheduler_without_a_card_is_a_bad_gateway(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        card_id = session.query(Flashcard).one().id

    with mock.patch.object(
        requests, "post", return_value=FakeResponse({"review_log": {}})
    ):
        response = client.post(
            "/review-flashcard",
            json={"flashcard_id": card_id, "rating": 3},
            headers=authorization(),
        )

    assert response.status_code == 502
