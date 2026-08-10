from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base
from shared.uuid_primary_key import UuidPrimaryKey

_USERNAME_LENGTH = 50
_EMAIL_LENGTH = 100
_HASHED_PASSWORD_LENGTH = 200


class User(UuidPrimaryKey, Base):
    __tablename__: str = "users"

    username: Mapped[str] = mapped_column(
        String(_USERNAME_LENGTH), unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String(_EMAIL_LENGTH), unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(_HASHED_PASSWORD_LENGTH)
    )
