from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.study_units.study_unit_access import owned_flashcard
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.identifiers import RowId

flashcard_editing_router = APIRouter()


class UpdateFlashcardRequest(BaseModel):
    flashcard_id: RowId
    content: dict[str, object]


@flashcard_editing_router.patch("/update-flashcard")
async def update_flashcard(
    request_data: UpdateFlashcardRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    card = owned_flashcard(db, user_id, request_data.flashcard_id)
    card.content = request_data.content
    db.commit()

    return JSONResponse(content={"msg": "Flashcard updated!"})


@flashcard_editing_router.delete("/delete-flashcard/")
async def delete_flashcard(
    flashcard_id: RowId,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    db.delete(owned_flashcard(db, user_id, flashcard_id))
    db.commit()

    return JSONResponse(content={"msg": "Flashcard deleted!"})
