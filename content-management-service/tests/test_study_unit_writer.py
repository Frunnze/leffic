import uuid

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation.assessment_writer import (
    append_test_items,
    create_test,
)
from features.study_units_generation.flashcard_deck_writer import (
    append_flashcards,
    create_flashcard_deck,
    name_deck_once,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import (
    PENDING_NAME,
    MissingFolderError,
    save_note,
)
from shared.models import Flashcard, FlashcardDeck, Folder, Note, Test
from tests.support import USER_ID, in_memory_sessions

HOME_ID = uuid.UUID(USER_ID)
_SOURCE = StudyUnitSource(kind="file", reference="biology.pdf")


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _home_folder(session: Session) -> None:
    session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
    session.commit()


def test_a_deck_is_saved_with_its_cards(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)

        deck_id = create_flashcard_deck(session, USER_ID, _SOURCE)
        _ = append_flashcards(
            session, deck_id, "basic", [{"front": "q", "back": "a"}]
        )
        _ = name_deck_once(session, deck_id, "Neurons")

    with sessions() as session:
        deck = session.query(FlashcardDeck).filter_by(id=deck_id).one()
        cards = session.query(Flashcard).all()

        assert deck.name == "Neurons"
        assert str(deck.folder_id) == USER_ID
        assert deck.source_kind == "file"
        assert deck.source_reference == "biology.pdf"
        assert len(cards) == 1
        assert cards[0].type == "basic"
        assert cards[0].content == {"front": "q", "back": "a"}


def test_a_new_deck_waits_for_its_name(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)
        deck_id = create_flashcard_deck(session, USER_ID, _SOURCE)

    with sessions() as session:
        deck = session.query(FlashcardDeck).filter_by(id=deck_id).one()

        assert deck.name == PENDING_NAME


def test_each_flashcard_type_keeps_its_own_name(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)
        deck_id = create_flashcard_deck(session, USER_ID, _SOURCE)
        _ = append_flashcards(
            session, deck_id, "basic", [{"front": "q", "back": "a"}]
        )
        _ = append_flashcards(
            session,
            deck_id,
            "cloze",
            [{"text": "t", "hidden_parts": ["t"]}],
        )

    with sessions() as session:
        types = {card.type for card in session.query(Flashcard).all()}

        assert types == {"basic", "cloze"}


def test_a_note_is_saved_with_its_content(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)

        note_id = save_note(
            session, USER_ID, "Neurons", "<p>Hi</p>", _SOURCE
        )

    with sessions() as session:
        note = session.query(Note).filter_by(id=note_id).one()

        assert note.name == "Neurons"
        assert note.content == "<p>Hi</p>"
        assert note.type == "general"
        assert str(note.folder_id) == USER_ID
        assert note.source_kind == "file"
        assert note.source_reference == "biology.pdf"


def test_a_test_is_saved_with_its_items(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _home_folder(session)

        test_id = create_test(session, USER_ID, _SOURCE)
        _ = append_test_items(
            session, test_id, "multiple_choice", [{"question": "q"}]
        )

    with sessions() as session:
        saved = session.query(Test).filter_by(id=test_id).one()

        assert str(saved.folder_id) == USER_ID
        assert saved.source_kind == "file"
        assert saved.source_reference == "biology.pdf"
        assert len(saved.test_items) == 1
        assert saved.test_items[0].type == "multiple_choice"
        assert saved.test_items[0].content == {"question": "q"}


def test_saving_into_a_missing_folder_is_refused(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session, pytest.raises(
        MissingFolderError
    ) as refusal:
        _ = save_note(
            session, str(uuid.uuid4()), "Ghost", "<p>Hi</p>", _SOURCE
        )

    assert str(refusal.value) == "Folder does not exist!"


def test_a_deck_needs_a_folder(sessions: sessionmaker[Session]) -> None:
    with sessions() as session, pytest.raises(MissingFolderError):
        _ = create_flashcard_deck(session, str(uuid.uuid4()), _SOURCE)


def test_a_test_needs_a_folder(sessions: sessionmaker[Session]) -> None:
    with sessions() as session, pytest.raises(MissingFolderError):
        _ = create_test(session, str(uuid.uuid4()), _SOURCE)
