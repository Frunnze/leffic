from typing import Self
from unittest import mock

import psycopg2
from sqlalchemy.orm import Session

from shared import database


class FakeCursor:
    def __init__(self, existing: tuple[int] | None) -> None:
        super().__init__()
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
        super().__init__()
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
        self.statements_before_autocommit = len(
            self.cursor_object.statements
        )

    def cursor(self) -> FakeCursor:
        return self.cursor_object

    def close(self) -> None:
        self.closed = True


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

    assert len(cursor.statements) == 2
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

    with mock.patch.object(
        psycopg2, "connect", return_value=connection
    ):
        database.create_database_if_not_exists()

    assert connection.autocommit
    assert connection.statements_before_autocommit == 0


def test_does_not_wrap_the_statements_in_a_transaction() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(
        psycopg2, "connect", return_value=connection
    ):
        database.create_database_if_not_exists()

    assert not connection.entered


def test_closes_the_connection() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(
        psycopg2, "connect", return_value=connection
    ):
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
