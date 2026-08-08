import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

_CASCADE_ORPHANS = "all, delete-orphan"


class FlashcardDeck(Base):
    __tablename__: str = "flashcard_decks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    folder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id"), nullable=False
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
        UUID(as_uuid=True),
        ForeignKey("flashcard_decks.id"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    next_review: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    content: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    fsrs_card: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True
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
        JSONB, nullable=False
    )
