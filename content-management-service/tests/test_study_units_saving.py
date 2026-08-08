import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from src.app_factory import create_app
from src.shared.database import get_db
from src.shared.models import Flashcard, Folder, Note, Test, TestItem
from tests.support import USER_ID, SessionProvider, in_memory_sessions

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


@pytest.fixture
def folder_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        session.add(Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID))
        session.commit()

    return str(_HOME_ID)


def test_saving_flashcards_creates_a_deck(
    client: TestClient, sessions: sessionmaker[Session], folder_id: str
) -> None:
    response = client.post(
        "/save-flashcards",
        json={
            "deck_name": "Cells",
            "folder_id": folder_id,
            "flashcards": {
                "basic_flashcards": [{"front": "q", "back": "a"}]
            },
        },
    )

    body = cast("dict[str, str]", response.json())

    with sessions() as session:
        stored = session.query(Flashcard).all()

    assert body["flashcard_deck_id"]
    assert stored[0].type == "basic"


def test_saving_flashcards_needs_an_existing_folder(
    client: TestClient,
) -> None:
    response = client.post(
        "/save-flashcards",
        json={
            "deck_name": "Cells",
            "folder_id": str(uuid.uuid4()),
            "flashcards": {},
        },
    )

    assert response.status_code == 404


def test_saving_a_note_stores_its_content(
    client: TestClient, sessions: sessionmaker[Session], folder_id: str
) -> None:
    response = client.post(
        "/save-note",
        json={
            "note_content": "<p>hello</p>",
            "note_name": "Intro",
            "folder_id": folder_id,
        },
    )

    with sessions() as session:
        stored = session.query(Note).one()

    assert response.status_code == 200
    assert stored.content == "<p>hello</p>"
    assert stored.type == "general"


def test_saving_a_test_stores_its_items(
    client: TestClient, sessions: sessionmaker[Session], folder_id: str
) -> None:
    response = client.post(
        "/save-test",
        json={
            "test_name": "Quiz",
            "folder_id": folder_id,
            "test_items": [{"question": "q", "true_option": "a"}],
        },
    )

    with sessions() as session:
        stored_test = session.query(Test).one()
        items = session.query(TestItem).all()

    assert response.status_code == 200
    assert stored_test.name == "Quiz"
    assert items[0].type == "mult_choice"
