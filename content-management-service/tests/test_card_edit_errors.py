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
    OTHER_USER_ID,
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

HOME_ID = uuid.UUID(USER_ID)
_OTHER_HOME_ID = uuid.UUID(OTHER_USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def home_folder(session: Session, user_id: uuid.UUID = HOME_ID) -> Folder:
    folder = Folder(id=user_id, name="Home", user_id=user_id)
    session.add(folder)
    session.commit()

    return folder


def deck(session: Session, name: str = "Deck") -> FlashcardDeck:
    created = FlashcardDeck(name=name, folder_id=HOME_ID)
    session.add(created)
    session.commit()

    return created


def test_a_missing_flashcard_says_so(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    response = client.patch(
        "/update-flashcard",
        json={"flashcard_id": 4242, "content": {"front": "New"}},
        headers=authorization(),
    )
    body = cast("dict[str, str]", response.json())

    assert body["detail"] == "Flashcard does not exist!"


def test_a_missing_test_item_says_so(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    response = client.patch(
        "/update-test-item",
        json={"test_item_id": 4242, "content": {"question": "New?"}},
        headers=authorization(),
    )
    body = cast("dict[str, str]", response.json())

    assert body["detail"] == "Test item does not exist!"


def test_updating_a_flashcard_leaves_the_others_alone(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        card_deck = deck(session)
        edited = Flashcard(
            deck_id=card_deck.id, type="basic", content={"front": "A"}
        )
        untouched = Flashcard(
            deck_id=card_deck.id, type="basic", content={"front": "B"}
        )
        session.add_all([edited, untouched])
        session.commit()
        edited_id = edited.id
        untouched_id = untouched.id

    _ = client.patch(
        "/update-flashcard",
        json={"flashcard_id": edited_id, "content": {"front": "Edited"}},
        headers=authorization(),
    )

    with sessions() as session:
        kept = session.query(Flashcard).filter_by(id=untouched_id).one()

        assert kept.content == {"front": "B"}
