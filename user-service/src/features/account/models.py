import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base
from shared.uuid_primary_key import UuidPrimaryKey

_PROVIDER_LENGTH = 30
_SEALED_KEY_LENGTH = 500
_SALT_LENGTH = 50
_HINT_LENGTH = 8


class ProviderKey(UuidPrimaryKey, Base):
    __tablename__: str = "provider_keys"
    __table_args__: tuple[UniqueConstraint, ...] = (
        UniqueConstraint("user_id", "provider", name="one_key_per_provider"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(
        String(_PROVIDER_LENGTH), nullable=False
    )
    sealed_key: Mapped[str] = mapped_column(
        String(_SEALED_KEY_LENGTH), nullable=False
    )
    salt: Mapped[str] = mapped_column(String(_SALT_LENGTH), nullable=False)
    hint: Mapped[str] = mapped_column(String(_HINT_LENGTH), nullable=False)
    monthly_limit_cents: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    spent_cents: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
