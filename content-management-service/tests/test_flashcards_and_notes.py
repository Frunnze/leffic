import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import Flashcard, FlashcardDeck, Folder
from tests.support import (
    USER_ID,
    FakeHTTPError,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_BAD_REQUEST = 400
_NOT_FOUND = 404
_OK = 200
_SUBMITTED_RATING = 3

_HOME_ID = uuid.UUID(USER_ID)


class FakeResponse:
    def __init__(
        self, payload: dict[str, object], status_code: int = 200
    ) -> None:
        super().__init__()
        self.payload: dict[str, object] = payload
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= _BAD_REQUEST:
            raise FakeHTTPError(self.status_code)

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


def test_due_flashcards_from_a_deck(client: TestClient, deck_id: str) -> None:
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

    assert response.status_code == _NOT_FOUND


def test_reviewing_a_flashcard_stores_the_schedule(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        card_id = session.query(Flashcard).one().id

    response = client.post(
        "/review-flashcard",
        json={"flashcard_id": card_id, "rating": _SUBMITTED_RATING},
        headers=authorization(),
    )
    body = cast("dict[str, object]", response.json())

    with sessions() as session:
        reviewed = session.query(Flashcard).one()
        stored_card = cast("dict[str, object]", reviewed.fsrs_card)

        stored_review = reviewed.flashcard_reviews[0].fsrs_review

        assert response.status_code == _OK
        assert body["due_date"]
        assert body["new_fsrs_card"] == stored_card
        assert reviewed.next_review is not None
        assert stored_card["due"]
        assert len(reviewed.flashcard_reviews) == 1
        assert stored_review["rating"] == _SUBMITTED_RATING


def test_reviewing_a_missing_flashcard_is_not_found(
    client: TestClient, deck_id: str
) -> None:
    assert deck_id

    response = client.post(
        "/review-flashcard",
        json={"flashcard_id": 4242, "rating": 3},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


def test_an_easier_rating_schedules_further_out(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        card_id = session.query(Flashcard).one().id

    _ = client.post(
        "/review-flashcard",
        json={"flashcard_id": card_id, "rating": 1},
        headers=authorization(),
    )

    with sessions() as session:
        after_again = session.query(Flashcard).one().next_review

    _ = client.post(
        "/review-flashcard",
        json={"flashcard_id": card_id, "rating": 4},
        headers=authorization(),
    )

    with sessions() as session:
        after_easy = session.query(Flashcard).one().next_review

    assert after_again is not None
    assert after_easy is not None
    assert after_easy > after_again
