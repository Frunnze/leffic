import uuid

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation.flashcard_deck_writer import (
    append_flashcards,
    create_flashcard_deck,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from shared.models import Flashcard, Folder
from tests.support import USER_ID, in_memory_sessions

HOME_ID = uuid.UUID(USER_ID)
_SOURCE = StudyUnitSource(kind="file", reference="biology.pdf")


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _home_folder(session: Session) -> None:
    session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
    session.commit()


def test_only_dictionary_cards_are_saved(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)
        deck_id = create_flashcard_deck(session, USER_ID, _SOURCE)
        _ = append_flashcards(
            session,
            deck_id,
            "basic",
            [{"front": "q", "back": "a"}, "junk"],
        )

    with sessions() as session:
        assert len(session.query(Flashcard).all()) == 1

def test_a_card_field_that_cannot_be_iterated_is_skipped(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)
        deck_id = create_flashcard_deck(session, USER_ID, _SOURCE)
        _ = append_flashcards(session, deck_id, "basic", 42)

    with sessions() as session:
        assert session.query(Flashcard).all() == []

def test_a_card_list_that_is_not_a_list_is_skipped(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)
        deck_id = create_flashcard_deck(session, USER_ID, _SOURCE)
        written = append_flashcards(session, deck_id, "basic", "oops")

    with sessions() as session:
        assert written == 0
        assert session.query(Flashcard).all() == []
