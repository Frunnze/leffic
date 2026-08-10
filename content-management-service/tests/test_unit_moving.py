import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import FlashcardDeck, Folder, Note, Test
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


def test_moving_a_note_changes_its_folder(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        destination = Folder(
            parent_id=HOME_ID, name="Biology", user_id=HOME_ID
        )
        note = Note(
            name="Note",
            folder_id=HOME_ID,
            type="summary",
            content="<p>Hi</p>",
        )
        session.add_all([destination, note])
        session.commit()
        destination_id = str(destination.id)
        note_id = str(note.id)

    response = client.patch(
        "/move-unit",
        json={
            "unit_id": note_id,
            "unit_type": "note",
            "folder_id": destination_id,
        },
        headers=authorization(),
    )

    assert response.status_code == 200

    with sessions() as session:
        moved = session.query(Note).filter_by(id=note_id).one()

        assert str(moved.folder_id) == destination_id


def test_moving_a_unit_home_resolves_the_root_folder(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        nested = Folder(parent_id=HOME_ID, name="Biology", user_id=HOME_ID)
        session.add(nested)
        session.commit()
        test_unit = Test(name="Test", folder_id=nested.id)
        session.add(test_unit)
        session.commit()
        test_id = str(test_unit.id)

    response = client.patch(
        "/move-unit",
        json={"unit_id": test_id, "unit_type": "test", "folder_id": "home"},
        headers=authorization(),
    )

    assert response.status_code == 200

    with sessions() as session:
        moved = session.query(Test).filter_by(id=test_id).one()

        assert str(moved.folder_id) == USER_ID


def test_moving_a_folder_changes_its_parent(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        destination = Folder(
            parent_id=HOME_ID, name="Biology", user_id=HOME_ID
        )
        moving = Folder(parent_id=HOME_ID, name="Cells", user_id=HOME_ID)
        session.add_all([destination, moving])
        session.commit()
        destination_id = str(destination.id)
        moving_id = str(moving.id)

    response = client.patch(
        "/move-unit",
        json={
            "unit_id": moving_id,
            "unit_type": "folder",
            "folder_id": destination_id,
        },
        headers=authorization(),
    )

    assert response.status_code == 200

    with sessions() as session:
        moved = session.query(Folder).filter_by(id=moving_id).one()

        assert str(moved.parent_id) == destination_id


def test_a_folder_cannot_be_moved_into_itself(
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

    assert response.status_code == 422


def test_moving_into_another_users_folder_is_not_found(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        _ = home_folder(session, _OTHER_HOME_ID)
        deck_id = str(deck(session).id)

    response = client.patch(
        "/move-unit",
        json={
            "unit_id": deck_id,
            "unit_type": "flashcard_deck",
            "folder_id": OTHER_USER_ID,
        },
        headers=authorization(),
    )

    assert response.status_code == 404
