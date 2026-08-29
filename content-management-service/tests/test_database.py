from unittest import mock

import psycopg2
import pytest
from sqlalchemy.orm import Session

from shared import database
from tests.database_bootstrap_support import (
    FakeConnection,
    FakeCursor,
)

_EXPECTED_STATEMENT_COUNT = 2


def test_get_db_yields_a_session_and_closes_it() -> None:
    sessions = database.get_db()
    session = next(sessions)

    assert isinstance(session, Session)

    sessions.close()


def test_creates_the_database_when_it_is_missing() -> None:
    cursor = FakeCursor(existing=None)

    connection = FakeConnection(cursor)

    with mock.patch.object(
        psycopg2, "connect", return_value=connection
    ) as connect:
        database.create_database_if_not_exists()

    assert len(cursor.statements) == _EXPECTED_STATEMENT_COUNT
    assert connect.call_args.kwargs == {
        "dbname": "postgres",
        "user": database.db_user,
        "password": database.db_pass,
        "host": database.db_host,
        "port": database.db_port,
    }


def test_leaves_an_existing_database_alone() -> None:
    cursor = FakeCursor(existing=(1,))

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ):
        database.create_database_if_not_exists()

    assert len(cursor.statements) == 1
    assert cursor.statements[0] == (
        "SELECT 1 FROM pg_database WHERE datname = %s"
    )
    assert cursor.parameters[0] == (database.db_name,)


def test_enables_autocommit_before_any_statement() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(psycopg2, "connect", return_value=connection):
        database.create_database_if_not_exists()

    assert connection.autocommit
    assert connection.statements_before_autocommit == 0


def test_does_not_wrap_the_statements_in_a_transaction() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(psycopg2, "connect", return_value=connection):
        database.create_database_if_not_exists()

    assert not connection.entered


def test_closes_the_connection() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(psycopg2, "connect", return_value=connection):
        database.create_database_if_not_exists()

    assert connection.closed


def test_the_create_statement_names_the_database() -> None:
    cursor = FakeCursor(existing=None)

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ):
        database.create_database_if_not_exists()

    assert str(cursor.statements[1]) == (
        "Composed([SQL('CREATE DATABASE '), "
        f"Identifier('{database.db_name}')])"
    )


_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5455/content"
_SQLITE_URL = "sqlite:///./content.db"


def _run_configured_bootstrap(
    database_url: str, connection: FakeConnection
) -> mock.MagicMock:
    with (
        mock.patch.object(
            database, "SQLALCHEMY_DATABASE_URL", database_url
        ),
        mock.patch.object(
            psycopg2, "connect", return_value=connection
        ) as connect,
    ):
        database.create_postgres_database_if_configured()

    return connect


def test_create_postgres_database_if_configured_connects_for_a_postgres_url(
) -> None:
    connection = FakeConnection(FakeCursor(existing=None))

    connect = _run_configured_bootstrap(_POSTGRES_URL, connection)

    assert connect.call_count == 1


def test_create_postgres_database_if_configured_skips_a_sqlite_url() -> None:
    connection = FakeConnection(FakeCursor(existing=None))

    connect = _run_configured_bootstrap(_SQLITE_URL, connection)

    assert connect.call_count == 0


def test_the_configured_bootstrap_runs_no_statement_for_a_sqlite_url(
) -> None:
    cursor = FakeCursor(existing=None)

    _ = _run_configured_bootstrap(_SQLITE_URL, FakeConnection(cursor))

    assert cursor.statements == []


def test_an_unreachable_postgres_propagates_the_operational_error() -> None:
    with (
        mock.patch.object(
            database, "SQLALCHEMY_DATABASE_URL", _POSTGRES_URL
        ),
        mock.patch.object(
            psycopg2, "connect", side_effect=psycopg2.OperationalError
        ),
        pytest.raises(psycopg2.OperationalError),
    ):
        database.create_postgres_database_if_configured()
