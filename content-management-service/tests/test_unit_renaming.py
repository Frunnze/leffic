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


def rename(
    client: TestClient, unit_id: str, unit_type: str, name: str
) -> tuple[int, dict[str, str]]:
    response = client.patch(
        "/rename-unit",
        json={"unit_id": unit_id, "unit_type": unit_type, "name": name},
        headers=authorization(),
    )

    return response.status_code, cast("dict[str, str]", response.json())


def test_renaming_a_deck_stores_the_new_name(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        deck_id = str(deck(session).id)

    code, _ = rename(client, deck_id, "flashcard_deck", "Action potentials")

    assert code == _OK

    with sessions() as session:
        renamed = session.query(FlashcardDeck).filter_by(id=deck_id).one()

        assert renamed.name == "Action potentials"


def test_renaming_a_folder_stores_the_new_name(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        folder = Folder(parent_id=HOME_ID, name="Old", user_id=HOME_ID)
        session.add(folder)
        session.commit()
        folder_id = str(folder.id)

    code, _ = rename(client, folder_id, "folder", "Neuroscience")

    assert code == _OK

    with sessions() as session:
        renamed = session.query(Folder).filter_by(id=folder_id).one()

        assert renamed.name == "Neuroscience"


def test_renaming_trims_the_name(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        deck_id = str(deck(session).id)

    _ = rename(client, deck_id, "flashcard_deck", "  Spaced  ")

    with sessions() as session:
        renamed = session.query(FlashcardDeck).filter_by(id=deck_id).one()

        assert renamed.name == "Spaced"


def test_renaming_leaves_the_other_units_alone(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        untouched_id = str(deck(session, "First").id)
        renamed_id = str(deck(session, "Second").id)

    _ = rename(client, renamed_id, "flashcard_deck", "Renamed")

    with sessions() as session:
        untouched = (
            session.query(FlashcardDeck).filter_by(id=untouched_id).one()
        )

        assert untouched.name == "First"
