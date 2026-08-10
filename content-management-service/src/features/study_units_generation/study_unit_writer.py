from collections.abc import Mapping, Sequence

from sqlalchemy.orm import Session

from shared.models import (
    Flashcard,
    FlashcardDeck,
    Folder,
    Note,
    Test,
    TestItem,
)

_FLASHCARDS_SUFFIX = "_flashcards"
_MISSING_FOLDER = "Folder does not exist!"


class MissingFolderError(Exception):
    def __init__(self) -> None:
        super().__init__(_MISSING_FOLDER)


def _owned_folder(db: Session, folder_id: str) -> Folder:
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
) -> str:
    folder = _owned_folder(db, folder_id)
    deck = FlashcardDeck(folder_id=folder.id, name=deck_name)
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
    db: Session, folder_id: str, note_name: str, note_content: str
) -> str:
    folder = _owned_folder(db, folder_id)
    note = Note(
        folder_id=folder.id,
        name=note_name,
        content=note_content,
        type="general",
    )
    db.add(note)
    db.commit()

    return str(note.id)


def save_test(
    db: Session,
    folder_id: str,
    test_name: str,
    test_items: list[dict[str, object]],
) -> str:
    folder = _owned_folder(db, folder_id)
    test = Test(folder_id=folder.id, name=test_name)
    db.add(test)

    for test_item in test_items:
        test.test_items.append(
            TestItem(content=test_item, type="mult_choice")
        )

    db.commit()

    return str(test.id)
