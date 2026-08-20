import uuid
from collections.abc import Iterator

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

_NOT_FOUND = 404
_OK = 200

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


def test_updating_a_flashcard_replaces_its_content(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        card_deck = deck(session)
        card = Flashcard(
            deck_id=card_deck.id,
            type="basic",
            content={"front": "Old", "back": "Older"},
        )
        session.add(card)
        session.commit()
        card_id = card.id

    response = client.patch(
        "/update-flashcard",
        json={
            "flashcard_id": card_id,
            "content": {"front": "New", "back": "Newer"},
        },
        headers=authorization(),
    )

    assert response.status_code == _OK

    with sessions() as session:
        updated = session.query(Flashcard).filter_by(id=card_id).one()

        assert updated.content == {"front": "New", "back": "Newer"}


def test_updating_a_missing_flashcard_is_not_found(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    response = client.patch(
        "/update-flashcard",
        json={"flashcard_id": 4242, "content": {"front": "New"}},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


def test_updating_another_users_flashcard_is_not_found(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        mine = deck(session, "Mine")
        session.add(
            Flashcard(deck_id=mine.id, type="basic", content={"a": "mine"})
        )
        session.commit()
        _ = home_folder(session, _OTHER_HOME_ID)
        deck_of_theirs = FlashcardDeck(name="Theirs", folder_id=_OTHER_HOME_ID)
        session.add(deck_of_theirs)
        session.commit()
        card = Flashcard(
            deck_id=deck_of_theirs.id, type="basic", content={"a": "b"}
        )
        session.add(card)
        session.commit()
        card_id = card.id

    response = client.patch(
        "/update-flashcard",
        json={"flashcard_id": card_id, "content": {"front": "Mine"}},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


def test_deleting_a_flashcard_removes_only_that_card(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        card_deck = deck(session)
        first = Flashcard(
            deck_id=card_deck.id, type="basic", content={"a": "1"}
        )
        second = Flashcard(
            deck_id=card_deck.id, type="basic", content={"a": "2"}
        )
        session.add_all([first, second])
        session.commit()
        first_id = first.id
        second_id = second.id

    response = client.delete(
        f"/delete-flashcard/?flashcard_id={first_id}",
        headers=authorization(),
    )

    assert response.status_code == _OK

    with sessions() as session:
        remaining = session.query(Flashcard).all()

        assert [card.id for card in remaining] == [second_id]


def test_deleting_a_missing_flashcard_is_not_found(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    response = client.delete(
        "/delete-flashcard/?flashcard_id=4242", headers=authorization()
    )

    assert response.status_code == _NOT_FOUND
