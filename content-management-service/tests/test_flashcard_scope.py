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


def test_cards_in_a_nested_subfolder_are_offered(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        child = Folder(parent_id=_HOME_ID, name="Sub", user_id=_HOME_ID)
        session.add(child)
        session.commit()
        grandchild = Folder(
            parent_id=child.id, name="Deep", user_id=_HOME_ID
        )
        session.add(grandchild)
        session.commit()
        deck = FlashcardDeck(folder_id=grandchild.id, name="Deep deck")
        deck.flashcards.append(Flashcard(type="basic", content={"q": "d"}))
        session.add(deck)
        session.commit()

    response = client.get(
        "/flashcards",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 2


def test_cards_under_a_folder_i_do_not_own_are_hidden(
    client: TestClient, sessions: sessionmaker[Session], deck_id: str
) -> None:
    assert deck_id

    with sessions() as session:
        home = session.query(Folder).filter_by(id=_HOME_ID).one()
        home.user_id = uuid.UUID(OTHER_USER_ID)
        session.commit()

    response = client.get(
        "/flashcards",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 0


def test_a_folder_card_due_tomorrow_is_not_offered(
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
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_flashcards"] == 0
