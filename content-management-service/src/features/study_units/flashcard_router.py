import uuid
from datetime import UTC, datetime
from typing import cast

import requests
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Query, Session

from src.features.study_units.formatting import date_to_str, flashcard_results
from src.shared.dependencies import AuthenticatedUserId, DatabaseSession
from src.shared.folder_tree import subfolder_ids
from src.shared.models import (
    Flashcard,
    FlashcardDeck,
    FlashcardReview,
)
from src.shared.settings import SCHEDULER_SERVICE

flashcard_router = APIRouter()

_HOME_FOLDER = "home"
_DEFAULT_PER_PAGE = 10
_MISSING_FOLDER = "Folder does not exist!"
_MISSING_FLASHCARD = "Flashcard does not exist!"
_SCHEDULER_TIMEOUT_SECONDS = 30


def _due_condition() -> ColumnElement[bool]:
    return or_(
        func.date(Flashcard.next_review) <= datetime.now(UTC).date(),
        Flashcard.next_review.is_(None),
    )


def _deck_flashcards(db: Session, deck_id: str) -> Query[Flashcard]:
    return db.query(Flashcard).filter(
        Flashcard.deck_id == uuid.UUID(deck_id), _due_condition()
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


@flashcard_router.get("/flashcards")
async def get_flashcards(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    flashcard_deck_id: str | None = None,
    folder_id: str | None = None,
    per_page: int = _DEFAULT_PER_PAGE,
) -> JSONResponse:
    if flashcard_deck_id:
        due_flashcards = _deck_flashcards(db, flashcard_deck_id)
    else:
        resolved_folder_id = (
            user_id if folder_id == _HOME_FOLDER else folder_id
        )

        if resolved_folder_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FOLDER
            )

        due_flashcards = _folder_flashcards(db, resolved_folder_id, user_id)

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

    # Call scheduler
    response = requests.post(
        url=f"{SCHEDULER_SERVICE}/schedule-flashcard",
        json={
            "card": card.fsrs_card,
            "rating": request_data.rating,
            "user_id": user_id,
        },
        timeout=_SCHEDULER_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    scheduled = cast("dict[str, object]", response.json())

    return JSONResponse(content=_recorded_review(db, card, scheduled))


def _recorded_review(
    db: Session, card: Flashcard, scheduled: dict[str, object]
) -> dict[str, object]:
    raw_new_card = scheduled.get("new_card")

    if not isinstance(raw_new_card, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Scheduler returned no card",
        )

    new_card = cast("dict[str, object]", raw_new_card)

    # Save new card
    card.fsrs_card = new_card
    next_review_date = datetime.fromisoformat(
        str(new_card.get("due"))
    ).replace(tzinfo=None)
    card.next_review = next_review_date

    # Add new card review log
    card.flashcard_reviews.append(
        FlashcardReview(fsrs_review=scheduled.get("review_log"))
    )
    db.commit()

    return {
        "due_date": date_to_str(next_review_date),
        "new_fsrs_card": new_card,
    }


