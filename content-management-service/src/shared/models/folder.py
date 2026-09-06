import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Constraint,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
)
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
_PARENT_FOREIGN_KEY = "Folder.parent_id"


class Folder(NamedRecord, Base):
    __tablename__: str = "folders"
    __table_args__: tuple[Constraint, ...] = (
        UniqueConstraint("id", "user_id", name="one_owner_per_folder"),
        ForeignKeyConstraint(
            ["parent_id", "user_id"],
            ["folders.id", "folders.user_id"],
            name="subfolder_shares_the_owner",
        ),
    )

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
        "Folder",
        remote_side="Folder.id",
        back_populates="subfolders",
        foreign_keys=_PARENT_FOREIGN_KEY,
    )
    subfolders: Mapped[list["Folder"]] = relationship(
        "Folder",
        back_populates="folder",
        cascade=_CASCADE_ORPHANS,
        foreign_keys=_PARENT_FOREIGN_KEY,
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
