from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.models import Flashcard, FlashcardDeck, Folder

flashcard_editing_router = APIRouter()

_MISSING_FLASHCARD = "Flashcard does not exist!"


def _owned_flashcard(
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
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FLASHCARD
        )

    return card


class UpdateFlashcardRequest(BaseModel):
    flashcard_id: int
    content: dict[str, object]


@flashcard_editing_router.patch("/update-flashcard")
async def update_flashcard(
    request_data: UpdateFlashcardRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    card = _owned_flashcard(db, user_id, request_data.flashcard_id)
    card.content = request_data.content
    db.commit()

    return JSONResponse(content={"msg": "Flashcard updated!"})


@flashcard_editing_router.delete("/delete-flashcard/")
async def delete_flashcard(
    flashcard_id: int,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    db.delete(_owned_flashcard(db, user_id, flashcard_id))
    db.commit()

    return JSONResponse(content={"msg": "Flashcard deleted!"})
