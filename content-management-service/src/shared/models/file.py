import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base
from shared.models.columns import FlexibleUuid


class File(Base):
    __tablename__: str = "files"

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
    extension: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
