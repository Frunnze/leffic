import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base

_USERNAME_LENGTH = 50
_EMAIL_LENGTH = 100
_HASHED_PASSWORD_LENGTH = 200


class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(_USERNAME_LENGTH), unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String(_EMAIL_LENGTH), unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(_HASHED_PASSWORD_LENGTH)
    )
