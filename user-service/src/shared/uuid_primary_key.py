import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column


class UuidPrimaryKey:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
