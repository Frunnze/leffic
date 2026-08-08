import uuid

from sqlalchemy.orm import Session

from src.shared.models import (
    File,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)

ContentEntry = dict[str, str]


def entries_in(
    db: Session, folder_id: str, user_id: str
) -> list[ContentEntry]:
    owner_id = uuid.UUID(user_id)
    entries: list[ContentEntry] = []
    entries.extend(_subfolders(db, folder_id, owner_id))
    entries.extend(_flashcard_decks(db, folder_id, owner_id))
    entries.extend(_tests(db, folder_id, owner_id))
    entries.extend(_files(db, folder_id, owner_id))
    entries.extend(_notes(db, folder_id))

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
        .join(Folder, FlashcardDeck.folder_id == Folder.id)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "flashcard_deck",
        }
        for row in rows
    ]


def _tests(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(Test)
        .join(Folder, Test.folder_id == Folder.id)
        .filter(Folder.id == folder_id, Folder.user_id == owner_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "test",
        }
        for row in rows
    ]


def _files(
    db: Session, folder_id: str, owner_id: uuid.UUID
) -> list[ContentEntry]:
    rows = (
        db.query(File)
        .join(Folder, File.folder_id == Folder.id)
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


def _notes(db: Session, folder_id: str) -> list[ContentEntry]:
    rows = (
        db.query(Note)
        .filter(Note.folder_id == folder_id)
        .all()
    )

    return [
        {
            "id": str(row.id),
            "name": row.name,
            "created_at": str(row.created_at),
            "type": "note",
        }
        for row in rows
    ]
