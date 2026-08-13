from collections.abc import Mapping, Sequence

from sqlalchemy.orm import Session

from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from shared.models import (
    Flashcard,
    FlashcardDeck,
    Folder,
    Note,
    Test,
    TestItem,
)

_FLASHCARDS_SUFFIX = "_flashcards"
_TEST_ITEMS_SUFFIX = "_test_items"
_MISSING_FOLDER = "Folder does not exist!"


class MissingFolderError(Exception):
    def __init__(self) -> None:
        super().__init__(_MISSING_FOLDER)


def _existing_folder(db: Session, folder_id: str) -> Folder:
    folder = db.query(Folder).filter_by(id=folder_id).first()

    if folder is None:
        raise MissingFolderError

    return folder


def _cards_of(cards: object) -> list[dict[str, object]]:
    if not isinstance(cards, Sequence) or isinstance(cards, str):
        return []

    return [card for card in cards if isinstance(card, dict)]


def save_flashcard_deck(
    db: Session,
    folder_id: str,
    deck_name: str,
    flashcards: Mapping[str, object],
    source: StudyUnitSource,
) -> str:
    folder = _existing_folder(db, folder_id)
    deck = FlashcardDeck(
        folder_id=folder.id,
        name=deck_name,
        source_kind=source.kind,
        source_reference=source.reference,
    )
    db.add(deck)

    for flashcard_type, cards in flashcards.items():
        cleaned_type = flashcard_type.replace(_FLASHCARDS_SUFFIX, "")

        for card in _cards_of(cards):
            deck.flashcards.append(
                Flashcard(type=cleaned_type, content=card)
            )

    db.commit()

    return str(deck.id)


def save_note(
    db: Session,
    folder_id: str,
    note_name: str,
    note_content: str,
    source: StudyUnitSource,
) -> str:
    folder = _existing_folder(db, folder_id)
    note = Note(
        folder_id=folder.id,
        name=note_name,
        content=note_content,
        type="general",
        source_kind=source.kind,
        source_reference=source.reference,
    )
    db.add(note)
    db.commit()

    return str(note.id)


def save_test(
    db: Session,
    folder_id: str,
    test_name: str,
    test_items: Mapping[str, object],
    source: StudyUnitSource,
) -> str:
    folder = _existing_folder(db, folder_id)
    test = Test(
        folder_id=folder.id,
        name=test_name,
        source_kind=source.kind,
        source_reference=source.reference,
    )
    db.add(test)

    for item_type, items in test_items.items():
        cleaned_type = item_type.replace(_TEST_ITEMS_SUFFIX, "")

        for test_item in _cards_of(items):
            test.test_items.append(
                TestItem(content=test_item, type=cleaned_type)
            )

    db.commit()

    return str(test.id)
