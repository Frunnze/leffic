from types import TracebackType
from typing import TYPE_CHECKING, final
from unittest import mock

import psycopg2
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app_factory import create_app
from shared import database

if TYPE_CHECKING:
    from fastapi import FastAPI

_PSYCOPG2_CONNECT_TARGET = "shared.database.psycopg2.connect"
_EXISTENCE_QUERY_ONLY = 1
_EXISTENCE_QUERY_AND_CREATE = 2
_EXPECTED_ROUTES = (
    "/chat",
    "/flashcards",
    "/test-items",
    "/note",
    "/create-folder",
    "/upload-files",
    "/extract-text",
)


@final
class RecordingCursor:
    def __init__(self, existing_row: tuple[int] | None) -> None:
        self.existing_row: tuple[int] | None = existing_row
        self.statements: list[object] = []

    def execute(
        self, statement: object, parameters: object = None
    ) -> None:
        _ = parameters
        self.statements.append(statement)

    def fetchone(self) -> tuple[int] | None:
        return self.existing_row

    def __enter__(self) -> "RecordingCursor":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


@final
class RecordingConnection:
    def __init__(self, existing_row: tuple[int] | None) -> None:
        self.opened_cursor: RecordingCursor = RecordingCursor(existing_row)
        self.autocommit: bool = False

    def cursor(self) -> RecordingCursor:
        return self.opened_cursor

    def close(self) -> None:
        return None


@final
class RecordingSession:
    def __init__(self) -> None:
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


@settings(max_examples=5, deadline=None)
@given(st.integers(min_value=1, max_value=3))
def test_create_app_property_mounts_every_router_on_a_fresh_app(
    count: int,
) -> None:
    apps: list[FastAPI] = []

    for _ in range(count):
        apps.append(create_app())

    assert len({id(app) for app in apps}) == count

    for app in apps:
        paths = {getattr(route, "path", "") for route in app.routes}

        assert set(_EXPECTED_ROUTES) <= paths


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=3))
def test_get_db_property_always_closes_the_session_it_opened(
    count: int,
) -> None:
    for _ in range(count):
        session = RecordingSession()

        with mock.patch.object(
            database, "SessionLocal", return_value=session
        ):
            opened = database.get_db()

            assert next(opened) is session
            assert not session.closed

            with pytest.raises(StopIteration):
                _ = next(opened)

        assert session.closed


@settings(max_examples=25)
@given(st.sampled_from([None, (1,)]))
def test_create_database_if_not_exists_property_creates_only_when_absent(
    existing_row: tuple[int] | None,
) -> None:
    connection = RecordingConnection(existing_row)

    with mock.patch(_PSYCOPG2_CONNECT_TARGET, return_value=connection):
        database.create_database_if_not_exists()

    expected_statements = _EXISTENCE_QUERY_ONLY
    if existing_row is None:
        expected_statements = _EXISTENCE_QUERY_AND_CREATE

    assert connection.autocommit
    assert len(connection.opened_cursor.statements) == expected_statements


_DATABASE_SCHEMES = (
    "postgresql",
    "postgresql+psycopg2",
    "postgres",
    "sqlite",
    "mysql",
    "PostgreSQL",
    "postgresq",
    "",
)


def _database_url(scheme: str, remainder: str) -> str:
    return f"{scheme}://{remainder}"


database_urls = st.builds(
    _database_url,
    st.sampled_from(_DATABASE_SCHEMES),
    st.text(max_size=20),
)
postgres_urls = st.builds(
    _database_url,
    st.sampled_from(("postgresql", "postgresql+psycopg2")),
    st.text(max_size=20),
)


@settings(max_examples=50, deadline=None)
@given(database_urls)
def test_create_postgres_database_if_configured_property_connects_for_postgres(
    database_url: str,
) -> None:
    connection = RecordingConnection(existing_row=(1,))

    with mock.patch(
        _PSYCOPG2_CONNECT_TARGET, return_value=connection
    ) as connect:
        database.create_postgres_database_if_configured(database_url)

    is_postgres_url = database_url.startswith(database._POSTGRES_SCHEME)

    assert bool(connect.call_count) is is_postgres_url


@settings(max_examples=25, deadline=None)
@given(postgres_urls)
def test_create_postgres_database_if_configured_property_propagates_the_error(
    database_url: str,
) -> None:
    with (
        mock.patch(
            _PSYCOPG2_CONNECT_TARGET,
            side_effect=psycopg2.OperationalError,
        ),
        pytest.raises(psycopg2.OperationalError),
    ):
        database.create_postgres_database_if_configured(database_url)
