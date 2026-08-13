import uuid
from datetime import datetime
from typing import cast

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fsrs.card import CardDict
from fsrs.review_log import ReviewLogDict
from pydantic import BaseModel
from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Query, Session

from features.study_units.formatting import date_to_str, flashcard_results
from shared.clock import utc_today
from shared.content_access import owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.flashcard_scheduling import (
    schedule_flashcard_fsrs,
)
from shared.folder_access import resolved_folder_id
from shared.folder_tree import subfolder_ids
from shared.models import (
    Flashcard,
    FlashcardDeck,
    FlashcardReview,
)

flashcard_router = APIRouter()

_DEFAULT_PER_PAGE = 10
_MISSING_FLASHCARD = "Flashcard does not exist!"
_MISSING_DECK = "Deck does not exist!"


def _due_condition() -> ColumnElement[bool]:
    return or_(
        func.date(Flashcard.next_review) <= utc_today(),
        Flashcard.next_review.is_(None),
    )


def _deck_flashcards(db: Session, deck_id: uuid.UUID) -> Query[Flashcard]:
    return db.query(Flashcard).filter(
        Flashcard.deck_id == deck_id, _due_condition()
    )


def _folder_flashcards(
    db: Session, folder_id: str, user_id: str
) -> Query[Flashcard]:
    deck_ids = select(FlashcardDeck.id).where(
        FlashcardDeck.folder_id.in_(subfolder_ids(folder_id, user_id))
    )

    return db.query(Flashcard).filter(
        Flashcard.deck_id.in_(deck_ids), _due_condition()
    )


def _due_flashcards(
    db: Session,
    user_id: str,
    flashcard_deck_id: str | None,
    folder_id: str | None,
) -> Query[Flashcard]:
    if flashcard_deck_id:
        deck = owned_content(
            db, user_id, FlashcardDeck, flashcard_deck_id, _MISSING_DECK
        )

        return _deck_flashcards(db, deck.id)

    return _folder_flashcards(
        db, resolved_folder_id(user_id, folder_id), user_id
    )


@flashcard_router.get("/flashcards")
async def get_flashcards(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    flashcard_deck_id: str | None = None,
    folder_id: str | None = None,
    per_page: int = _DEFAULT_PER_PAGE,
) -> JSONResponse:
    due_flashcards = _due_flashcards(
        db, user_id, flashcard_deck_id, folder_id
    )

    flashcards = (
        due_flashcards.order_by(Flashcard.next_review.asc().nullsfirst())
        .limit(per_page)
        .all()
    )

    return JSONResponse(
        content={
            "flashcards": flashcard_results(flashcards),
            "total_flashcards": due_flashcards.count(),
        }
    )


class ReviewFlashcardRequest(BaseModel):
    flashcard_id: int
    rating: int


@flashcard_router.post("/review-flashcard")
def review_flashcard(
    request_data: ReviewFlashcardRequest,
    db: DatabaseSession,
    user_id: AuthenticatedUserId,
) -> JSONResponse:
    # Get card
    card = (
        db.query(Flashcard).filter_by(id=request_data.flashcard_id).first()
    )

    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FLASHCARD
        )

    _ = user_id
    new_card, review_log = schedule_flashcard_fsrs(
        cast("CardDict | None", card.fsrs_card), None, request_data.rating
    )

    return JSONResponse(
        content=_recorded_review(db, card, new_card, review_log)
    )


def _recorded_review(
    db: Session,
    card: Flashcard,
    new_card: CardDict,
    review_log: ReviewLogDict,
) -> dict[str, object]:
    card.fsrs_card = dict(new_card)
    next_review_date = datetime.fromisoformat(
        str(new_card["due"])
    ).replace(tzinfo=None)
    card.next_review = next_review_date

    card.flashcard_reviews.append(
        FlashcardReview(fsrs_review=dict(review_log))
    )
    db.commit()

    return {
        "due_date": date_to_str(next_review_date),
        "new_fsrs_card": new_card,
    }


