from collections.abc import Sequence

from sqlalchemy.orm import Session

from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from shared.models import Folder, Note

_MISSING_FOLDER = "Folder does not exist!"

PENDING_NAME = "Generating…"


def generated_records(generated: object) -> list[dict[str, object]]:
    if not isinstance(generated, Sequence) or isinstance(generated, str):
        return []

    return [record for record in generated if isinstance(record, dict)]


class MissingFolderError(Exception):
    def __init__(self) -> None:
        super().__init__(_MISSING_FOLDER)


def existing_folder(db: Session, folder_id: str) -> Folder:
    folder = db.query(Folder).filter_by(id=folder_id).first()

    if folder is None:
        raise MissingFolderError

    return folder


def save_note(
    db: Session,
    folder_id: str,
    note_name: str,
    note_content: str,
    source: StudyUnitSource,
) -> str:
    folder = existing_folder(db, folder_id)
    note = Note(
        folder_id=folder.id,
        name=note_name,
        content=note_content,
        type="general",
        source_kind=source.kind,
        source_reference=source.reference,
    )
    db.add(note)
    db.commit()

    return str(note.id)
