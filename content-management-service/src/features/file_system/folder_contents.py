import uuid

from sqlalchemy.orm import Session

from shared.models import (
    File,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)
from shared.models.mixins import FolderContent, GeneratedContent

ContentEntry = dict[str, str]


def _source_of(row: GeneratedContent) -> ContentEntry:
    if row.source_kind is None:
        return {}

    return {
        "source_kind": row.source_kind,
        "source_reference": row.source_reference or "",
    }


def entries_in(
    db: Session, folder_id: str, user_id: str
) -> list[ContentEntry]:
    owner_id = uuid.UUID(user_id)
    flashcard_decks = _generated_entries(
        db, folder_id, owner_id, FlashcardDeck, "flashcard_deck"
    )
    tests = _generated_entries(db, folder_id, owner_id, Test, "test")
    notes = _generated_entries(db, folder_id, owner_id, Note, "note")

    return [
        *_subfolders(db, folder_id, owner_id),
        *flashcard_decks,
        *tests,
        *_files(db, folder_id, owner_id),
        *notes,
    ]


def _subfolders(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(Folder)
        .filter(Folder.parent_id == folder_id, Folder.user_id == owner_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "folder",
        }
        for row in rows
    ]


def _rows_in_folder[ContentT: FolderContent](
    db: Session,
    model: type[ContentT],
    folder_id: str,
    owner_id: uuid.UUID,
) -> list[ContentT]:
    return (
        db.query(model)
        .join(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )


def _generated_entries(
    db: Session,
    folder_id: str,
    owner_id: uuid.UUID,
    model: type[GeneratedContent],
    entry_type: str,
) -> list[ContentEntry]:
    rows = _rows_in_folder(db, model, folder_id, owner_id)

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": entry_type,
            **_source_of(row),
        }
        for row in rows
    ]


def _files(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = _rows_in_folder(db, File, folder_id, owner_id)

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "extension": str(row.extension),
            "type": "file",
        }
        for row in rows
    ]
