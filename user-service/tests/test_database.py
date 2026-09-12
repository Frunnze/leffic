import importlib
import os
from unittest import mock

from sqlalchemy.orm import Session

from shared import database

_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/users"


def test_get_db_yields_a_session_and_closes_it() -> None:
    sessions = database.get_db()
    session = next(sessions)

    assert isinstance(session, Session)

    sessions.close()


def test_the_session_factory_is_bound_to_the_engine() -> None:
    assert database.SessionLocal.kw["bind"] is database.engine


def test_importing_the_module_opens_no_administrative_connection() -> None:
    with (
        mock.patch.dict(os.environ, {"DATABASE_URL": _POSTGRES_URL}),
        mock.patch.object(database, "create_engine"),
        mock.patch("psycopg2.connect") as connect,
    ):
        _ = importlib.reload(database)

        assert not connect.called

    _ = importlib.reload(database)
