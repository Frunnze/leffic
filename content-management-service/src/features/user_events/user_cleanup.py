import uuid

from sqlalchemy.orm import Session

from shared.file_storage import delete_file_from_storage
from shared.models import File, Folder


def _stored_file_names(db: Session, user_id: uuid.UUID) -> list[str]:
    files = (
        db.query(File)
        .join(Folder)
        .filter(Folder.user_id == user_id)
        .all()
    )

    return [f"{file.id}.{file.extension}" for file in files]


def remove_everything_owned_by(db: Session, user_id: str) -> int:
    owner = uuid.UUID(user_id)
    stored_names = _stored_file_names(db, owner)
    folders = db.query(Folder).filter(Folder.user_id == owner).all()

    for folder in folders:
        db.delete(folder)

    db.commit()

    for stored_name in stored_names:
        delete_file_from_storage(stored_name)

    return len(folders)
