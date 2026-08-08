import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base
from shared.models.columns import FlexibleUuid

_CASCADE_ORPHANS = "all, delete-orphan"


class FlashcardDeck(Base):
    __tablename__: str = "flashcard_decks"

    id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    folder_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(), ForeignKey("folders.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    flashcards: Mapped[list["Flashcard"]] = relationship(
        backref="deck", cascade=_CASCADE_ORPHANS
    )


class Flashcard(Base):
    __tablename__: str = "flashcards"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    deck_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(),
        ForeignKey("flashcard_decks.id"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    next_review: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    content: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    fsrs_card: Mapped[dict[str, object] | None] = mapped_column(
        JSON, nullable=True
    )

    flashcard_reviews: Mapped[list["FlashcardReview"]] = relationship(
        backref="flashcard", cascade=_CASCADE_ORPHANS
    )


class FlashcardReview(Base):
    __tablename__: str = "flashcard_reviews"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    flashcard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flashcards.id"), nullable=False
    )
    fsrs_review: Mapped[dict[str, object]] = mapped_column(
        JSON, nullable=False
    )
