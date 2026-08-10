import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import FlashcardDeck, Folder
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


def test_a_circular_move_is_refused_with_a_reason(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        folder = Folder(parent_id=HOME_ID, name="Cells", user_id=HOME_ID)
        session.add(folder)
        session.commit()
        folder_id = str(folder.id)

    response = client.patch(
        "/move-unit",
        json={
            "unit_id": folder_id,
            "unit_type": "folder",
            "folder_id": folder_id,
        },
        headers=authorization(),
    )
    body = cast("dict[str, str]", response.json())

    assert body["detail"] == "A folder cannot be moved inside itself!"


def test_another_users_folder_cannot_be_moved(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        _ = home_folder(session, _OTHER_HOME_ID)
        theirs = Folder(
            parent_id=_OTHER_HOME_ID, name="Theirs", user_id=_OTHER_HOME_ID
        )
        session.add(theirs)
        session.commit()
        folder_id = str(theirs.id)

    response = client.patch(
        "/move-unit",
        json={
            "unit_id": folder_id,
            "unit_type": "folder",
            "folder_id": "home",
        },
        headers=authorization(),
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == 404
    assert body["detail"] == "Unit does not exist!"


def test_moving_leaves_the_other_units_alone(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        destination = Folder(
            parent_id=HOME_ID, name="Biology", user_id=HOME_ID
        )
        session.add(destination)
        session.commit()
        moved_id = str(deck(session, "Moved").id)
        stayed_id = str(deck(session, "Stayed").id)
        destination_id = str(destination.id)

    _ = client.patch(
        "/move-unit",
        json={
            "unit_id": moved_id,
            "unit_type": "flashcard_deck",
            "folder_id": destination_id,
        },
        headers=authorization(),
    )

    with sessions() as session:
        stayed = session.query(FlashcardDeck).filter_by(id=stayed_id).one()

        assert str(stayed.folder_id) == USER_ID
