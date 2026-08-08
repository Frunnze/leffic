from typing import Self
from unittest import mock

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.orm import Session

from src.shared import database


class FakeCursor:
    def __init__(self, existing: tuple[int] | None) -> None:
        super().__init__()
        self.existing: tuple[int] | None = existing
        self.statements: list[object] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, statement: object, *_: object) -> None:
        self.statements.append(statement)

    def fetchone(self) -> tuple[int] | None:
        return self.existing


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        super().__init__()
        self.cursor_object: FakeCursor = cursor
        self.isolation_level: int | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def set_isolation_level(self, level: int) -> None:
        self.isolation_level = level

    def cursor(self) -> FakeCursor:
        return self.cursor_object


def test_get_db_yields_a_session_and_closes_it() -> None:
    sessions = database.get_db()
    session = next(sessions)

    assert isinstance(session, Session)

    sessions.close()


def test_creates_the_database_when_it_is_missing() -> None:
    cursor = FakeCursor(existing=None)

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ):
        database.create_database_if_not_exists()

    assert len(cursor.statements) == 2


def test_leaves_an_existing_database_alone() -> None:
    cursor = FakeCursor(existing=(1,))

    with mock.patch.object(
        psycopg2, "connect", return_value=FakeConnection(cursor)
    ):
        database.create_database_if_not_exists()

    assert len(cursor.statements) == 1


def test_sets_autocommit_before_creating() -> None:
    cursor = FakeCursor(existing=None)
    connection = FakeConnection(cursor)

    with mock.patch.object(
        psycopg2, "connect", return_value=connection
    ):
        database.create_database_if_not_exists()

    assert connection.isolation_level == ISOLATION_LEVEL_AUTOCOMMIT
