
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import ColumnElement, func, or_, select

from shared.clock import utc_today
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import owned_folder_id
from shared.folder_tree import subfolder_ids
from shared.models import Flashcard, FlashcardDeck

flashcard_stats_router = APIRouter()

_NO_FLASHCARDS = "No flashcards!"


def _due_condition() -> ColumnElement[bool]:
    return or_(
        func.date(Flashcard.next_review) <= utc_today(),
        Flashcard.next_review.is_(None),
    )


@flashcard_stats_router.get("/flashcards-stats")
async def get_flashcards_stats(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    folder_id: str | None = None,
) -> JSONResponse:
    resolved_folder_id = owned_folder_id(db, user_id, folder_id)

    deck_ids = select(FlashcardDeck.id).where(
        FlashcardDeck.folder_id.in_(
            subfolder_ids(resolved_folder_id, user_id)
        )
    )
    due_flashcards = (
        db.query(Flashcard)
        .filter(Flashcard.deck_id.in_(deck_ids), _due_condition())
        .count()
    )
    done_flashcards = (
        db.query(Flashcard)
        .filter(
            Flashcard.deck_id.in_(deck_ids),
            func.date(Flashcard.next_review) > utc_today(),
            Flashcard.next_review.is_not(None),
        )
        .count()
    )

    if due_flashcards == 0 and done_flashcards == 0:
        return JSONResponse(
            content={"msg": _NO_FLASHCARDS},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return JSONResponse(
        content={"due": due_flashcards, "done": done_flashcards}
    )
