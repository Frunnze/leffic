from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.models import File, Folder

_MISSING_FILE = "File does not exist!"


def owned_file(db: Session, user_id: str, file_id: str) -> File:
    owned = db.execute(
        select(File)
        .join(Folder)
        .where(Folder.user_id == user_id, File.id == file_id)
    ).scalar_one_or_none()

    if owned is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FILE
        )

    return owned
