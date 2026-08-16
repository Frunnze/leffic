from sqlalchemy.orm import Session

from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import (
    PENDING_NAME,
    existing_folder,
    generated_records,
)
from shared.models import Flashcard, FlashcardDeck

_MISSING_DECK = "Flashcard deck does not exist!"


class MissingDeckError(Exception):
    def __init__(self) -> None:
        super().__init__(_MISSING_DECK)


def _existing_deck(db: Session, deck_id: str) -> FlashcardDeck:
    deck = db.query(FlashcardDeck).filter_by(id=deck_id).first()

    if deck is None:
        raise MissingDeckError

    return deck


def create_flashcard_deck(
    db: Session, folder_id: str, source: StudyUnitSource
) -> str:
    folder = existing_folder(db, folder_id)
    deck = FlashcardDeck(
        folder_id=folder.id,
        name=PENDING_NAME,
        source_kind=source.kind,
        source_reference=source.reference,
    )
    db.add(deck)
    db.commit()

    return str(deck.id)


def append_flashcards(
    db: Session, deck_id: str, flashcard_type: str, cards: object
) -> int:
    deck = _existing_deck(db, deck_id)
    appended = generated_records(cards)

    for card in appended:
        deck.flashcards.append(
            Flashcard(type=flashcard_type, content=card)
        )

    db.commit()

    return len(appended)


def name_deck_once(db: Session, deck_id: str, deck_name: str) -> bool:
    named = (
        db.query(FlashcardDeck)
        .filter(
            FlashcardDeck.id == deck_id,
            FlashcardDeck.name == PENDING_NAME,
        )
        .update({FlashcardDeck.name: deck_name})
    )
    db.commit()

    return bool(named)
