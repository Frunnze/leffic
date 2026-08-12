import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.content_access import ContentModel, ContentUnit, owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import owned_folder, owned_folder_id
from shared.folder_tree import subfolder_ids
from shared.models import File, FlashcardDeck, Folder, Note, Test

unit_router = APIRouter()

_FOLDER_TYPE = "folder"
_CONTENT_MODELS: dict[str, ContentModel] = {
    "flashcard_deck": FlashcardDeck,
    "test": Test,
    "note": Note,
    "file": File,
}
_MISSING_UNIT = "Unit does not exist!"
_UNKNOWN_UNIT_TYPE = "Unknown unit type!"
_BLANK_NAME = "Name cannot be blank!"
_CIRCULAR_MOVE = "A folder cannot be moved inside itself!"


class RenameUnitRequest(BaseModel):
    unit_id: str
    unit_type: str
    name: str


class MoveUnitRequest(BaseModel):
    unit_id: str
    unit_type: str
    folder_id: str


def _content_model(unit_type: str) -> ContentModel:
    model = _CONTENT_MODELS.get(unit_type)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_UNKNOWN_UNIT_TYPE,
        )

    return model


def _owned_unit(
    db: Session, user_id: str, unit_id: str, unit_type: str
) -> ContentUnit:
    return owned_content(
        db, user_id, _content_model(unit_type), unit_id, _MISSING_UNIT
    )


def _validated_name(name: str) -> str:
    trimmed = name.strip()

    if not trimmed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_BLANK_NAME,
        )

    return trimmed


@unit_router.patch("/rename-unit")
async def rename_unit(
    request_data: RenameUnitRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    name = _validated_name(request_data.name)

    if request_data.unit_type == _FOLDER_TYPE:
        unit: Folder | ContentUnit = owned_folder(
            db, user_id, request_data.unit_id, _MISSING_UNIT
        )
    else:
        unit = _owned_unit(
            db, user_id, request_data.unit_id, request_data.unit_type
        )

    unit.name = name
    db.commit()

    return JSONResponse(content={"msg": "Unit renamed!"})


@unit_router.patch("/move-unit")
async def move_unit(
    request_data: MoveUnitRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    destination_id = owned_folder_id(db, user_id, request_data.folder_id)

    if request_data.unit_type == _FOLDER_TYPE:
        _move_folder(db, user_id, request_data.unit_id, destination_id)
    else:
        unit = _owned_unit(
            db, user_id, request_data.unit_id, request_data.unit_type
        )
        unit.folder_id = uuid.UUID(destination_id)

    db.commit()

    return JSONResponse(content={"msg": "Unit moved!"})


def _move_folder(
    db: Session, user_id: str, unit_id: str, destination_id: str
) -> None:
    folder = owned_folder(db, user_id, unit_id, _MISSING_UNIT)
    subtree = db.execute(subfolder_ids(unit_id)).scalars().all()

    if uuid.UUID(destination_id) in subtree:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_CIRCULAR_MOVE,
        )

    folder.parent_id = uuid.UUID(destination_id)
