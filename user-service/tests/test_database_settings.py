import importlib
import os
from unittest import mock

from shared import database_settings

_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/users"


def _reload_with(environment: dict[str, str]) -> None:
    with mock.patch.dict(os.environ, environment):
        _ = importlib.reload(database_settings)


def test_an_explicit_url_wins_over_the_assembled_one() -> None:
    _reload_with({"DATABASE_URL": _POSTGRES_URL})

    assert database_settings.SQLALCHEMY_DATABASE_URL == _POSTGRES_URL

    _ = importlib.reload(database_settings)


def test_the_assembled_url_carries_every_connection_setting() -> None:
    _reload_with(
        {
            "DATABASE_URL": "",
            "DB_USER": "carol",
            "DB_PASS": "secret",
            "DB_HOST": "db.internal",
            "DB_PORT": "6000",
        }
    )

    assert database_settings.SQLALCHEMY_DATABASE_URL == (
        "postgresql://carol:secret@db.internal:6000/users"
    )

    _ = importlib.reload(database_settings)


def test_the_database_is_named_after_the_service() -> None:
    assert database_settings.DATABASE_NAME == "users"
