import importlib
import os
from typing import cast
from unittest import mock

import pytest

from shared import database, jwt_secret


def test_a_missing_jwt_secret_stops_the_service_from_starting() -> None:
    with (
        mock.patch.dict(os.environ, {"JWT_SECRET_KEY": ""}),
        pytest.raises(RuntimeError, match="JWT_SECRET_KEY"),
    ):
        _ = importlib.reload(jwt_secret)

    _ = importlib.reload(jwt_secret)


_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/content"
_OTHER_POSTGRES_URL = "postgresql://reader:secret@db.internal:6543/library"
_SQLITE_URL = "sqlite://"
_PSYCOPG2_CONNECT_TARGET = "psycopg2.connect"


def _reload_with_database_url(database_url: str) -> tuple[str, mock.Mock]:
    with (
        mock.patch.dict(os.environ, {"DATABASE_URL": database_url}),
        mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect,
    ):
        reloaded = importlib.reload(database)
        configured_url = cast("str", reloaded.SQLALCHEMY_DATABASE_URL)

    _ = importlib.reload(database)

    return configured_url, connect


def test_a_postgres_url_does_not_bootstrap_the_database_at_import() -> None:
    configured_url, connect = _reload_with_database_url(_POSTGRES_URL)

    assert configured_url == _POSTGRES_URL
    assert connect.call_count == 0


def test_a_sqlite_url_does_not_bootstrap_the_database_at_import() -> None:
    configured_url, connect = _reload_with_database_url(_SQLITE_URL)

    assert configured_url == _SQLITE_URL
    assert connect.call_count == 0


def test_the_configured_database_url_survives_the_module_import() -> None:
    configured_url, _ = _reload_with_database_url(_OTHER_POSTGRES_URL)

    assert configured_url == _OTHER_POSTGRES_URL
