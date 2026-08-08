import uuid
from collections.abc import Iterator

import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from shared.database import Base

USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
OTHER_USER_ID = "6f1c7d4e-0000-4000-8000-0000000000ff"


class SessionProvider:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        super().__init__()
        self.session_factory: sessionmaker[Session] = session_factory

    def __call__(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()


def in_memory_sessions() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    return sessionmaker(bind=engine)


def authorization(user_id: str = USER_ID) -> dict[str, str]:
    token = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


def as_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)
