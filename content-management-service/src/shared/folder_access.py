from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.models import Folder

_HOME_FOLDER = "home"
_MISSING_FOLDER = "Folder does not exist!"


def owned_folder_id(
    db: Session, user_id: str, folder_id: str | None
) -> str:
    resolved = user_id if folder_id == _HOME_FOLDER else folder_id

    owned = db.execute(
        select(Folder.id).where(
            Folder.user_id == user_id, Folder.id == resolved
        )
    ).scalar_one_or_none()

    if owned is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FOLDER
        )

    return str(owned)
