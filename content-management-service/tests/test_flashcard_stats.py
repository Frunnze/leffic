import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import Flashcard, FlashcardDeck, Folder
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    FakeHTTPError,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_BAD_REQUEST = 400
_NOT_FOUND = 404

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


def test_flashcard_stats_count_due_and_done(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        deck = session.query(FlashcardDeck).one()
        deck.flashcards.append(
            Flashcard(
                type="basic",
                content={"q": "b"},
                next_review=datetime.now(UTC) + timedelta(days=5),
            )
        )
        session.commit()

    response = client.get(
        "/flashcards-stats",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    body = cast("dict[str, int]", response.json())

    assert body == {"due": 1, "done": 1}


def test_flashcard_stats_need_an_owned_folder(client: TestClient) -> None:
    response = client.get(
        "/flashcards-stats",
        params={"folder_id": str(uuid.uuid4())},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


def test_flashcard_stats_report_nothing_for_an_empty_folder(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID))
        session.commit()

    response = client.get(
        "/flashcards-stats",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND
    assert cast("dict[str, str]", response.json())["msg"] == "No flashcards!"


def test_stats_treat_a_card_due_today_as_due(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        session.query(Flashcard).one().next_review = datetime.now(UTC)
        session.commit()

    response = client.get(
        "/flashcards-stats",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, int]", response.json()) == {"due": 1, "done": 0}


def test_stats_ignore_another_users_cards(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        stranger = uuid.UUID(OTHER_USER_ID)
        session.add(Folder(id=stranger, name="Home", user_id=stranger))
        deck = FlashcardDeck(folder_id=stranger, name="Theirs")
        deck.flashcards.append(Flashcard(type="basic", content={"q": "c"}))
        session.add(deck)
        session.commit()

    response = client.get(
        "/flashcards-stats",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, int]", response.json()) == {"due": 1, "done": 0}
