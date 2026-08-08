import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base
from src.shared.models.columns import FlexibleUuid

_CASCADE_ORPHANS = "all, delete-orphan"


class Test(Base):
    __tablename__: str = "tests"

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

    test_items: Mapped[list["TestItem"]] = relationship(
        backref="test", cascade=_CASCADE_ORPHANS
    )


class TestItem(Base):
    __tablename__: str = "test_items"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(), ForeignKey("tests.id"), nullable=False
    )
    content: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )

    test_item_reviews: Mapped[list["TestItemReview"]] = relationship(
        backref="test_item",
        cascade=_CASCADE_ORPHANS,
        order_by="TestItemReview.reviewed_at",
    )


class TestSession(Base):
    __tablename__: str = "test_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    origin_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(), nullable=False
    )  # test/folder id
    status: Mapped[str] = mapped_column(
        String, nullable=False
    )  # done/ongoing
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=True
    )


class TestItemReview(Base):
    __tablename__: str = "test_item_reviews"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    test_session: Mapped[uuid.UUID] = mapped_column(
        FlexibleUuid(), ForeignKey("test_sessions.id"), nullable=False
    )
    test_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_items.id"), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=True
    )
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    answers: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
