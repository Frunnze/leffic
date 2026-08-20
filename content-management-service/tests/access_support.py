import uuid
from collections.abc import Iterator
from typing import NamedTuple, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.content_access import ContentModel
from shared.database import get_db
from shared.models import (
    File,
    Flashcard,
    FlashcardDeck,
    Folder,
    Note,
    Test,
    TestItem,
    TestSession,
)
from tests.support import OTHER_USER_ID, USER_ID, SessionProvider

HOME_ID = uuid.UUID(USER_ID)
OTHER_HOME_ID = uuid.UUID(OTHER_USER_ID)

MISSING_UNIT = "Unit does not exist!"
MISSING_FILE = "File does not exist!"
MISSING_FOLDER = "Folder does not exist!"
MISSING_NOTE = "Note does not exist!"
MISSING_DECK = "Deck does not exist!"
MISSING_TEST = "Test does not exist!"
PROTECTED_HOME = "Home folder cannot be deleted!"

QUESTION: dict[str, object] = {
    "question": "Which is a mammal?",
    "true_option": "whale",
    "false_options": ["shark", "trout"],
}


class ScopedRoute(NamedTuple):
    method: str
    path: str
    parameter: str
    attribute: str
    detail: str


class OwnedContent(NamedTuple):
    home_id: str
    folder_id: str
    deck_id: str
    test_id: str
    note_id: str
    file_id: str


def _wired_app(sessions: sessionmaker[Session]) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    return app


def scoped_client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    with TestClient(_wired_app(sessions)) as test_client:
        yield test_client


def crashless_client(
    sessions: sessionmaker[Session],
) -> Iterator[TestClient]:
    client = TestClient(
        _wired_app(sessions), raise_server_exceptions=False
    )

    with client as test_client:
        yield test_client


def seeded_content(
    sessions: sessionmaker[Session], owner: uuid.UUID
) -> OwnedContent:
    with sessions() as session:
        return _seeded_units(session, _seeded_folder(session, owner))


def _seeded_folder(session: Session, owner: uuid.UUID) -> Folder:
    session.add(Folder(id=owner, name="Home", user_id=owner))
    session.commit()

    folder = Folder(parent_id=owner, name="Sub", user_id=owner)
    session.add(folder)
    session.commit()

    return folder


def _seeded_units(session: Session, folder: Folder) -> OwnedContent:
    deck = FlashcardDeck(folder_id=folder.id, name="Deck")
    deck.flashcards.append(Flashcard(type="basic", content={"q": "a"}))
    quiz = Test(folder_id=folder.id, name="Quiz")
    quiz.test_items.append(TestItem(content=QUESTION, type="mult_choice"))
    note = Note(
        folder_id=folder.id, name="N", content="body", type="general"
    )
    stored = File(folder_id=folder.id, name="doc", extension="pdf")
    session.add_all([deck, quiz, note, stored])
    session.commit()

    return OwnedContent(
        home_id=str(folder.parent_id),
        folder_id=str(folder.id),
        deck_id=str(deck.id),
        test_id=str(quiz.id),
        note_id=str(note.id),
        file_id=str(stored.id),
    )


def unit_identifier(content: OwnedContent, attribute: str) -> str:
    return cast("str", getattr(content, attribute))


def identifier_spellings(value: str) -> tuple[str, ...]:
    parsed = uuid.UUID(value)

    return (
        str(parsed),
        str(parsed).upper(),
        "{" + str(parsed) + "}",
        parsed.urn,
        parsed.hex,
    )


def _decoded(response: Response) -> dict[str, str]:
    if response.headers.get("content-type") != "application/json":
        return {"detail": response.text}

    return cast("dict[str, str]", response.json())


def delete_unit(
    client: TestClient,
    path: str,
    parameter: str,
    unit_id: str,
    headers: dict[str, str],
) -> tuple[int, dict[str, str]]:
    response = client.request(
        "DELETE", path, params={parameter: unit_id}, headers=headers
    )

    return response.status_code, _decoded(response)


def read_unit(
    client: TestClient,
    path: str,
    parameter: str,
    unit_id: str,
    headers: dict[str, str],
) -> tuple[int, dict[str, object]]:
    response = client.get(
        path, params={parameter: unit_id}, headers=headers
    )

    return response.status_code, cast(
        "dict[str, object]", _decoded(response)
    )


def surviving_ids(
    sessions: sessionmaker[Session], model: ContentModel
) -> set[str]:
    with sessions() as session:
        rows = session.query(model).all()

    return {str(row.id) for row in rows}


def surviving_folder_ids(sessions: sessionmaker[Session]) -> set[str]:
    with sessions() as session:
        rows = session.query(Folder).all()

    return {str(row.id) for row in rows}


def opened_test_sessions(sessions: sessionmaker[Session]) -> int:
    with sessions() as session:
        return session.query(TestSession).count()
