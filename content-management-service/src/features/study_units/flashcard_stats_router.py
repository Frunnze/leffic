from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import ColumnElement, func, or_, select

from src.shared.dependencies import AuthenticatedUserId, DatabaseSession
from src.shared.folder_tree import subfolder_ids
from src.shared.models import Flashcard, FlashcardDeck, Folder

flashcard_stats_router = APIRouter()

_HOME_FOLDER = "home"
_NO_FLASHCARDS = "No flashcards!"
_MISSING_FOLDER = "Folder does not exist!"


def _due_condition() -> ColumnElement[bool]:
    return or_(
        func.date(Flashcard.next_review) <= datetime.now(UTC).date(),
        Flashcard.next_review.is_(None),
    )


@flashcard_stats_router.get("/flashcards-stats")
async def get_flashcards_stats(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    folder_id: str | None = None,
) -> JSONResponse:
    resolved_folder_id = user_id if folder_id == _HOME_FOLDER else folder_id

    user_folder_exists = (
        db.query(Folder)
        .filter(Folder.user_id == user_id, Folder.id == resolved_folder_id)
        .first()
    )

    if not user_folder_exists or resolved_folder_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FOLDER
        )

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
            func.date(Flashcard.next_review)
            > datetime.now(UTC).date(),
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
