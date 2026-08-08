import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.shared.models.assessment import Test
    from src.shared.models.file import File
    from src.shared.models.flashcard import FlashcardDeck
    from src.shared.models.note import Note

_CASCADE_ORPHANS = "all, delete-orphan"


class Folder(Base):
    __tablename__: str = "folders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    folder: Mapped["Folder | None"] = relationship(
        "Folder", remote_side="Folder.id", back_populates="subfolders"
    )
    subfolders: Mapped[list["Folder"]] = relationship(
        "Folder", back_populates="folder", cascade=_CASCADE_ORPHANS
    )

    files: Mapped[list["File"]] = relationship(
        backref="folder", cascade=_CASCADE_ORPHANS
    )
    flashcard_decks: Mapped[list["FlashcardDeck"]] = relationship(
        backref="folder", cascade=_CASCADE_ORPHANS
    )
    tests: Mapped[list["Test"]] = relationship(
        backref="folder", cascade=_CASCADE_ORPHANS
    )
    notes: Mapped[list["Note"]] = relationship(
        backref="folder", cascade=_CASCADE_ORPHANS
    )
