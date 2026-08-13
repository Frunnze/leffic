import uuid
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared import file_storage
from shared.database import get_db
from shared.models import (
    File,
    Flashcard,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def _home_folder(session: Session) -> Folder:
    folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
    session.add(folder)
    session.commit()

    return folder


def test_deleting_a_deck_removes_its_flashcards(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        deck = FlashcardDeck(folder_id=folder.id, name="Deck")
        deck.flashcards.append(Flashcard(type="basic", content={"q": "a"}))
        session.add(deck)
        session.commit()
        deck_id = str(deck.id)

    response = client.request(
        "DELETE",
        "/delete-deck/",
        params={"deck_id": deck_id},
        headers=authorization(),
    )

    assert response.json() == {"msg": "Deck deleted!"}


def test_deleting_a_test(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        quiz = Test(folder_id=folder.id, name="Quiz")
        session.add(quiz)
        session.commit()
        test_id = str(quiz.id)

    response = client.request(
        "DELETE",
        "/delete-test/",
        params={"test_id": test_id},
        headers=authorization(),
    )

    assert response.json() == {"msg": "Test deleted!"}


def test_deleting_a_note(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        note = Note(
            folder_id=folder.id, name="N", content="c", type="general"
        )
        session.add(note)
        session.commit()
        note_id = str(note.id)

    response = client.request(
        "DELETE",
        "/delete-note/",
        params={"note_id": note_id},
        headers=authorization(),
    )

    assert response.json() == {"msg": "Note deleted!"}


def test_deleting_a_file_removes_it_from_storage(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        stored = File(folder_id=folder.id, name="doc", extension="pdf")
        session.add(stored)
        session.commit()
        file_id = str(stored.id)

    _ = (tmp_path / f"{file_id}.pdf").write_bytes(b"payload")

    with mock.patch.object(file_storage, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.request(
            "DELETE",
            "/delete-file/",
            params={"file_id": file_id},
            headers=authorization(),
        )

    assert response.json() == {"msg": "File deleted!"}
    assert not (tmp_path / f"{file_id}.pdf").exists()


def test_deleting_an_unknown_file_is_not_found(client: TestClient) -> None:
    response = client.request(
        "DELETE",
        "/delete-file/",
        params={"file_id": str(uuid.uuid4())},
        headers=authorization(),
    )

    assert response.status_code == 404
