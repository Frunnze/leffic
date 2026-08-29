from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from shared.models import (
    Flashcard,
    FlashcardDeck,
    Folder,
    Test,
    TestItem,
)

_MISSING_FLASHCARD = "Flashcard does not exist!"
MISSING_TEST_ITEM = "Test item does not exist!"


def owned_flashcard(
    db: Session, user_id: str, flashcard_id: int
) -> Flashcard:
    card = (
        db.query(Flashcard)
        .join(FlashcardDeck)
        .join(Folder)
        .filter(Flashcard.id == flashcard_id, Folder.user_id == user_id)
        .first()
    )

    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_MISSING_FLASHCARD,
        )

    return card


def owned_test_item(
    db: Session, user_id: str, test_item_id: int
) -> TestItem:
    item = (
        db.query(TestItem)
        .join(Test)
        .join(Folder)
        .filter(TestItem.id == test_item_id, Folder.user_id == user_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MISSING_TEST_ITEM,
        )

    return item
