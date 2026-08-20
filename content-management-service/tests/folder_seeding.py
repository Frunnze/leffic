import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from shared.models import File, FlashcardDeck, Folder, Note, Test

KINDS = ("flashcard_deck", "test", "file", "note", "folder")


def seeded_folder(
    session: Session,
    owner: uuid.UUID,
    counts: dict[str, int],
    source_kind: str | None = None,
) -> uuid.UUID:
    folder = Folder(
        id=uuid.uuid4(),
        name="root",
        user_id=owner,
        created_at=datetime.now(UTC),
        public=False,
    )
    session.add(folder)
    session.flush()

    for index in range(counts.get("folder", 0)):
        session.add(
            Folder(
                id=uuid.uuid4(),
                name=f"child-{index}",
                user_id=owner,
                parent_id=folder.id,
                created_at=datetime.now(UTC),
                public=False,
            )
        )

    _add_generated(session, folder.id, counts, source_kind)
    _add_files(session, folder.id, counts.get("file", 0))
    session.commit()

    return folder.id


def _add_generated(
    session: Session,
    folder_id: uuid.UUID,
    counts: dict[str, int],
    source_kind: str | None,
) -> None:
    extras: dict[str, dict[str, object]] = {
        "flashcard_deck": {},
        "test": {},
        "note": {"content": "body", "type": "summary", "read": False},
    }
    models = {
        "flashcard_deck": FlashcardDeck,
        "test": Test,
        "note": Note,
    }

    for kind, model in models.items():
        for index in range(counts.get(kind, 0)):
            session.add(
                model(
                    id=uuid.uuid4(),
                    name=f"{kind}-{index}",
                    folder_id=folder_id,
                    created_at=datetime.now(UTC),
                    public=False,
                    source_kind=source_kind,
                    source_reference=None,
                    **extras[kind],
                )
            )


def _add_files(
    session: Session, folder_id: uuid.UUID, count: int
) -> None:
    for index in range(count):
        session.add(
            File(
                id=uuid.uuid4(),
                name=f"file-{index}",
                folder_id=folder_id,
                created_at=datetime.now(UTC),
                public=False,
                extension="pdf",
            )
        )
