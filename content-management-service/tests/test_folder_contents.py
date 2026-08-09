import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.file_system.folder_contents import entries_in
from shared.models import (
    File,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)
from tests.support import USER_ID, in_memory_sessions

_HOME_ID = uuid.UUID(USER_ID)
_MADE_AT = datetime(2026, 8, 8, 17, 0, 0)  # noqa: DTZ001
_MADE_AT_TEXT = "2026-08-08 17:00:00"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _home(session: Session) -> Folder:
    folder = Folder(
        id=_HOME_ID, name="Home", user_id=_HOME_ID, created_at=_MADE_AT
    )
    session.add(folder)
    session.commit()

    return folder


def _entries(sessions: sessionmaker[Session]) -> list[dict[str, str]]:
    with sessions() as session:
        return entries_in(session, str(_HOME_ID), USER_ID)


def test_a_subfolder_is_described_in_full(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _ = _home(session)
        child = Folder(
            parent_id=_HOME_ID,
            name="Biology",
            user_id=_HOME_ID,
            created_at=_MADE_AT,
        )
        session.add(child)
        session.commit()
        child_id = str(child.id)

    assert _entries(sessions) == [
        {
            "id": child_id,
            "name": "Biology",
            "created_at": _MADE_AT_TEXT,
            "type": "folder",
        }
    ]


def test_a_deck_is_described_in_full(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _ = _home(session)
        deck = FlashcardDeck(
            folder_id=_HOME_ID, name="Cells", created_at=_MADE_AT
        )
        session.add(deck)
        session.commit()
        deck_id = str(deck.id)

    assert _entries(sessions) == [
        {
            "id": deck_id,
            "name": "Cells",
            "created_at": _MADE_AT_TEXT,
            "type": "flashcard_deck",
        }
    ]


def test_a_test_is_described_in_full(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _ = _home(session)
        quiz = Test(folder_id=_HOME_ID, name="Quiz", created_at=_MADE_AT)
        session.add(quiz)
        session.commit()
        quiz_id = str(quiz.id)

    assert _entries(sessions) == [
        {
            "id": quiz_id,
            "name": "Quiz",
            "created_at": _MADE_AT_TEXT,
            "type": "test",
        }
    ]


def test_a_file_is_described_in_full(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _ = _home(session)
        stored = File(
            folder_id=_HOME_ID,
            name="notes",
            extension="pdf",
            created_at=_MADE_AT,
        )
        session.add(stored)
        session.commit()
        file_id = str(stored.id)

    assert _entries(sessions) == [
        {
            "id": file_id,
            "name": "notes",
            "created_at": _MADE_AT_TEXT,
            "extension": "pdf",
            "type": "file",
        }
    ]


def test_a_note_is_described_in_full(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _ = _home(session)
        note = Note(
            folder_id=_HOME_ID,
            name="Intro",
            content="body",
            type="general",
            created_at=_MADE_AT,
        )
        session.add(note)
        session.commit()
        note_id = str(note.id)

    assert _entries(sessions) == [
        {
            "id": note_id,
            "name": "Intro",
            "created_at": _MADE_AT_TEXT,
            "type": "note",
        }
    ]
