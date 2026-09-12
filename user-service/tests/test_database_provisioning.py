from typing import Self
from unittest import mock

import psycopg2

import database_provisioning
from shared import database_settings

_EXPECTED_STATEMENT_COUNT = 2


class FakeCursor:
    def __init__(self, existing: tuple[int] | None) -> None:
        self.existing: tuple[int] | None = existing
        self.statements: list[object] = []
        self.parameters: list[object] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, statement: object, *arguments: object) -> None:
        self.statements.append(statement)
        self.parameters.extend(arguments)

    def fetchone(self) -> tuple[int] | None:
        return self.existing


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor_object: FakeCursor = cursor
        self.entered: bool = False
        self.closed: bool = False
        self.statements_before_autocommit: int | None = None
        self._autocommit: bool = False

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, *_: object) -> None:
        return None

    @property
    def autocommit(self) -> bool:
        return self._autocommit

    @autocommit.setter
    def autocommit(self, enabled: bool) -> None:
        self._autocommit = enabled
        self.statements_before_autocommit = len(self.cursor_object.statements)

    def cursor(self) -> FakeCursor:
        return self.cursor_object

    def close(self) -> None:
        self.closed = True


def test_creates_the_database_when_it_is_missing() -> None:
    cursor = FakeCursor(existing=None)

    connection = FakeConnection(cursor)

    with mock.patch.object(
        psycopg2, "connect", return_value=connection
    ) as connect:
        database_provisioning.create_database_if_not_exists()

    assert len(cursor.statements) == _EXPECTED_STATEMENT_COUNT
    assert connect.call_args.kwargs == {
        "dbname": "postgres",
        "user": database_settings.DATABASE_USER,
        "password": database_settings.DATABASE_PASSWORD,
        "host": database_settings.DATABASE_HOST,
        "port": database_settings.DATABASE_PORT,
    }


def test_leaves_an_existing_database_alone() -> None:
    cursor = FakeCursor(existing=(1,))

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ):
        database_provisioning.create_database_if_not_exists()

    assert len(cursor.statements) == 1
    assert cursor.statements[0] == (
        "SELECT 1 FROM pg_database WHERE datname = %s"
    )
    assert cursor.parameters[0] == (database_settings.DATABASE_NAME,)


def test_enables_autocommit_before_any_statement() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(psycopg2, "connect", return_value=connection):
        database_provisioning.create_database_if_not_exists()

    assert connection.autocommit
    assert connection.statements_before_autocommit == 0


def test_does_not_wrap_the_statements_in_a_transaction() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(psycopg2, "connect", return_value=connection):
        database_provisioning.create_database_if_not_exists()

    assert not connection.entered


def test_closes_the_connection() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(psycopg2, "connect", return_value=connection):
        database_provisioning.create_database_if_not_exists()

    assert connection.closed


def test_the_create_statement_names_the_database() -> None:
    cursor = FakeCursor(existing=None)

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ):
        database_provisioning.create_database_if_not_exists()

    assert str(cursor.statements[1]) == (
        "Composed([SQL('CREATE DATABASE '), "
        f"Identifier('{database_settings.DATABASE_NAME}')])"
    )


def test_a_postgres_url_provisions_the_database() -> None:
    cursor = FakeCursor(existing=(1,))

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ) as connect:
        database_provisioning.create_postgres_database_if_configured(
            "postgresql://postgres:postgres@localhost:5432/users"
        )

    assert connect.call_count == 1


def test_a_sqlite_url_provisions_nothing() -> None:
    with mock.patch.object(psycopg2, "connect") as connect:
        database_provisioning.create_postgres_database_if_configured(
            "sqlite:///local.db"
        )

    assert not connect.called
