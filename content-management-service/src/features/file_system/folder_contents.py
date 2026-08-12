import uuid

from sqlalchemy.orm import Session

from shared.models import (
    File,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)
from shared.models.mixins import GeneratedContent

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
    entries: list[ContentEntry] = []
    entries.extend(_subfolders(db, folder_id, owner_id))
    entries.extend(_flashcard_decks(db, folder_id, owner_id))
    entries.extend(_tests(db, folder_id, owner_id))
    entries.extend(_files(db, folder_id, owner_id))
    entries.extend(_notes(db, folder_id, owner_id))

    return entries


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


def _flashcard_decks(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(FlashcardDeck)
        .join(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "flashcard_deck",
            **_source_of(row),
        }
        for row in rows
    ]


def _tests(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(Test)
        .join(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "test",
            **_source_of(row),
        }
        for row in rows
    ]


def _files(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(File)
        .join(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )

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


def _notes(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(Note)
        .join(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "note",
            **_source_of(row),
        }
        for row in rows
    ]
