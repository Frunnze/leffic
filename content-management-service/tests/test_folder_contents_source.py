import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.file_system.folder_contents import entries_in
from shared.models import FlashcardDeck, Folder, Note, Test
from tests.support import USER_ID, in_memory_sessions

_HOME_ID = uuid.UUID(USER_ID)
_MADE_AT = datetime(2026, 8, 8, 17, 0, 0)  # noqa: DTZ001


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(
            Folder(
                id=_HOME_ID,
                name="Home",
                user_id=_HOME_ID,
                created_at=_MADE_AT,
            )
        )
        session.commit()

    return factory


def _entries(sessions: sessionmaker[Session]) -> list[dict[str, str]]:
    with sessions() as session:
        return entries_in(session, str(_HOME_ID), USER_ID)


def test_every_generated_unit_reports_where_it_came_from(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        session.add_all(
            [
                Note(
                    folder_id=_HOME_ID,
                    name="Rome",
                    content="<p>Hi</p>",
                    type="general",
                    created_at=_MADE_AT,
                    source_kind="topic",
                    source_reference="roman empire",
                ),
                FlashcardDeck(
                    folder_id=_HOME_ID,
                    name="Rome cards",
                    created_at=_MADE_AT,
                    source_kind="file",
                    source_reference="rome.pdf",
                ),
                Test(
                    folder_id=_HOME_ID,
                    name="Rome test",
                    created_at=_MADE_AT,
                    source_kind="link",
                    source_reference="https://example.com/rome",
                ),
            ]
        )
        session.commit()

    origins = {
        entry["type"]: (entry["source_kind"], entry["source_reference"])
        for entry in _entries(sessions)
    }

    assert origins == {
        "note": ("topic", "roman empire"),
        "flashcard_deck": ("file", "rome.pdf"),
        "test": ("link", "https://example.com/rome"),
    }


def test_a_unit_without_a_source_reports_none(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        session.add(
            Note(
                folder_id=_HOME_ID,
                name="Rome",
                content="<p>Hi</p>",
                type="general",
                created_at=_MADE_AT,
            )
        )
        session.commit()

    entry = _entries(sessions)[0]

    assert "source_kind" not in entry
    assert "source_reference" not in entry


def test_a_source_without_a_reference_reports_an_empty_one(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        session.add(
            Note(
                folder_id=_HOME_ID,
                name="Rome",
                content="<p>Hi</p>",
                type="general",
                created_at=_MADE_AT,
                source_kind="text",
            )
        )
        session.commit()

    entry = _entries(sessions)[0]

    assert entry["source_kind"] == "text"
    assert entry["source_reference"] == ""
