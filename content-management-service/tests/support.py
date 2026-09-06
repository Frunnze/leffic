import uuid
from collections.abc import Iterator
from contextlib import closing

import jwt
import requests
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry, StaticPool

from shared.database import Base
from shared.jwt_secret import ALGORITHM, SECRET_KEY

USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
OTHER_USER_ID = "6f1c7d4e-0000-4000-8000-0000000000ff"
_ENABLE_FOREIGN_KEYS = "PRAGMA foreign_keys=ON"


class FakeHTTPError(requests.HTTPError):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"status {status_code}")


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


def _in_memory_engine() -> Engine:
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def in_memory_sessions() -> sessionmaker[Session]:
    engine = _in_memory_engine()
    Base.metadata.create_all(bind=engine)

    return sessionmaker(bind=engine)


def _enable_foreign_keys(
    connection: DBAPIConnection,
    _connection_pool_entry: ConnectionPoolEntry,
) -> None:
    with closing(connection.cursor()) as cursor:
        cursor.execute(_ENABLE_FOREIGN_KEYS)


def foreign_key_enforcing_sessions() -> sessionmaker[Session]:
    engine = _in_memory_engine()
    event.listen(engine, "connect", _enable_foreign_keys)
    Base.metadata.create_all(bind=engine)

    return sessionmaker(bind=engine)


def authorization(user_id: str = USER_ID) -> dict[str, str]:
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)

    return {"Authorization": f"Bearer {token}"}


def as_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)
