import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base
from shared.models.columns import FlexibleUuid
from shared.models.mixins import NamedRecord

if TYPE_CHECKING:
    from shared.models.assessment import Test
    from shared.models.file import File
    from shared.models.flashcard import FlashcardDeck
    from shared.models.note import Note

_CASCADE_ORPHANS = "all, delete-orphan"


class Folder(NamedRecord, Base):
    __tablename__: str = "folders"

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        FlexibleUuid(),
        ForeignKey("folders.id"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(), nullable=False
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
