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


def rename(
    client: TestClient, unit_id: str, unit_type: str, name: str
) -> tuple[int, dict[str, str]]:
    response = client.patch(
        "/rename-unit",
        json={"unit_id": unit_id, "unit_type": unit_type, "name": name},
        headers=authorization(),
    )

    return response.status_code, cast("dict[str, str]", response.json())


def test_a_blank_name_is_refused_with_a_reason(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        deck_id = str(deck(session).id)

    code, body = rename(client, deck_id, "flashcard_deck", "   ")

    assert code == 422
    assert body["detail"] == "Name cannot be blank!"


def test_an_unknown_unit_type_is_refused_with_a_reason(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        deck_id = str(deck(session).id)

    code, body = rename(client, deck_id, "recipe", "Nope")

    assert code == 422
    assert body["detail"] == "Unknown unit type!"


def test_a_malformed_id_reads_as_a_missing_unit(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    code, body = rename(client, "not-a-uuid", "flashcard_deck", "Nope")

    assert code == 404
    assert body["detail"] == "Unit does not exist!"


def test_a_missing_folder_reads_as_a_missing_unit(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    code, body = rename(client, str(uuid.uuid4()), "folder", "Ghost")

    assert code == 404
    assert body["detail"] == "Unit does not exist!"


def test_another_users_deck_cannot_be_renamed(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        _ = home_folder(session, _OTHER_HOME_ID)
        theirs = FlashcardDeck(name="Theirs", folder_id=_OTHER_HOME_ID)
        session.add(theirs)
        session.commit()
        deck_id = str(theirs.id)

    code, body = rename(client, deck_id, "flashcard_deck", "Mine now")

    assert code == 404
    assert body["detail"] == "Unit does not exist!"


def test_another_users_folder_cannot_be_renamed(
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

    code, body = rename(client, folder_id, "folder", "Mine now")

    assert code == 404
    assert body["detail"] == "Unit does not exist!"
