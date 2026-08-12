import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.identifiers import parsed_identifier
from shared.models import Folder

_HOME_FOLDER = "home"
MISSING_FOLDER = "Folder does not exist!"


def resolved_folder_id(user_id: str, folder_id: str | None) -> str:
    resolved = user_id if folder_id == _HOME_FOLDER else folder_id

    if resolved is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MISSING_FOLDER
        )

    _ = parsed_identifier(resolved, MISSING_FOLDER)

    return resolved


def owned_folder_id(
    db: Session, user_id: str, folder_id: str | None
) -> str:
    resolved = resolved_folder_id(user_id, folder_id)

    owned = db.execute(
        select(Folder.id).where(
            Folder.user_id == user_id, Folder.id == resolved
        )
    ).scalar_one_or_none()

    if owned is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MISSING_FOLDER
        )

    return str(owned)


def owned_folder(
    db: Session, user_id: str, folder_id: str, missing_detail: str
) -> Folder:
    folder = (
        db.query(Folder)
        .filter(
            Folder.id == parsed_identifier(folder_id, missing_detail),
            Folder.user_id == user_id,
        )
        .first()
    )

    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=missing_detail
        )

    return folder


def ensured_home_folder(db: Session, user_id: str) -> Folder:
    home = db.query(Folder).filter_by(id=user_id).first()

    if home is not None:
        return home

    created = Folder(
        id=uuid.UUID(user_id), name="Home", user_id=uuid.UUID(user_id)
    )
    db.add(created)
    db.commit()

    return created
