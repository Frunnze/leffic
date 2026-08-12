import re
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from features.file_system.file_storage import delete_file_from_storage
from features.file_system.folder_contents import entries_in
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import (
    MISSING_FOLDER,
    ensured_home_folder,
    owned_folder,
    owned_folder_id,
)
from shared.folder_tree import subfolder_ids
from shared.identifiers import parsed_identifier
from shared.models import File, Folder

folder_router = APIRouter()

_HOME_FOLDER = "home"
_CREATED_AT_FORMAT = "%Y-%m-%dT%H:%M:%S"
_PROTECTED_HOME = "Home folder cannot be deleted!"


class CreateFolderRequest(BaseModel):
    parent_folder_id: str | None = None
    folder_name: str = "New folder"


def _available_folder_name(
    db: Session, parent_folder_id: str, folder_name: str
) -> str:
    numbered_name = re.compile(
        rf"^{re.escape(folder_name)}\s*(\d+)?\s*$"
    )
    siblings = (
        db.query(Folder)
        .filter(Folder.parent_id == parent_folder_id)
        .all()
    )

    # Count folders with the same name
    same_name_folders_num = sum(
        1 for sibling in siblings if numbered_name.match(sibling.name)
    )

    # Set the name
    if same_name_folders_num:
        return f"{folder_name} {same_name_folders_num + 1}"

    return folder_name


def _owned_parent_id(
    db: Session, user_id: str, parent_folder_id: str
) -> str:
    if parent_folder_id == _HOME_FOLDER:
        return str(ensured_home_folder(db, user_id).id)

    return owned_folder_id(db, user_id, parent_folder_id)


@folder_router.post("/create-folder")
async def create_folder(
    request_data: CreateFolderRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    if request_data.parent_folder_id is None:
        return JSONResponse(
            status_code=422, content={"detail": "Missing parent folder"}
        )

    parent_folder_id = _owned_parent_id(
        db, user_id, request_data.parent_folder_id
    )

    folder_name = _available_folder_name(
        db, parent_folder_id, request_data.folder_name
    )

    # Create the row
    new_folder = Folder(
        parent_id=uuid.UUID(parent_folder_id),
        name=folder_name,
        user_id=uuid.UUID(user_id),
        created_at=datetime.now(UTC),
    )
    db.add(new_folder)
    db.commit()

    return JSONResponse(
        content={
            "folder_id": str(new_folder.id),
            "parent_folder_id": parent_folder_id,
            "folder_name": folder_name,
            "created_at": new_folder.created_at.strftime(_CREATED_AT_FORMAT),
        }
    )


def _files_storage_ids(db: Session, folder_id: str) -> list[str]:
    files = (
        db.query(File)
        .where(File.folder_id.in_(subfolder_ids(folder_id)))
        .all()
    )

    return [f"{file.id}.{file.extension}" for file in files]


@folder_router.delete("/delete-folder/")
async def delete_folder(
    folder_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    folder = owned_folder(db, user_id, folder_id, MISSING_FOLDER)

    if folder.id == folder.user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_PROTECTED_HOME,
        )

    files_storage_ids = _files_storage_ids(db, str(folder.id))

    # Delete the main folder
    db.delete(folder)
    db.commit()

    # Delete the files
    for file_storage_id in files_storage_ids:
        delete_file_from_storage(file_storage_id)

    return JSONResponse(content={"msg": "Folder deleted!"})


@folder_router.get("/access-folder/")
async def access_folder(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    folder_id: str | None = None,
) -> JSONResponse:
    if folder_id == _HOME_FOLDER:
        return _home_folder_response(db, user_id)

    if folder_id is None:
        return JSONResponse(
            status_code=422, content={"detail": "Missing folder id"}
        )

    identifier = parsed_identifier(folder_id, MISSING_FOLDER)
    folder = (
        db.query(Folder)
        .filter(Folder.id == identifier, Folder.user_id == user_id)
        .first()
    )

    return JSONResponse(
        content={
            "content": entries_in(db, folder_id, user_id),
            "parent_folder_name": folder.name if folder else "Home",
        }
    )


def _home_folder_response(db: Session, user_id: str) -> JSONResponse:
    folder = ensured_home_folder(db, user_id)

    return JSONResponse(
        content={
            "content": entries_in(db, str(folder.id), user_id),
            "parent_folder_name": folder.name,
        }
    )
