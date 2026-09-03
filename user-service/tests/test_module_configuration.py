import importlib
import os
from typing import cast
from unittest import mock

import pytest
from hypothesis import given, strategies

from features.authentication import cookie_security
from shared import database, jwt_secret


def test_a_missing_jwt_secret_stops_the_service_from_starting() -> None:
    with (
        mock.patch.dict(os.environ, {"JWT_SECRET_KEY": ""}),
        pytest.raises(RuntimeError, match="JWT_SECRET_KEY"),
    ):
        _ = importlib.reload(jwt_secret)

    _ = importlib.reload(jwt_secret)


def test_a_postgres_url_bootstraps_the_database() -> None:
    postgres_url = "postgresql://postgres:postgres@localhost:5432/users"

    with (
        mock.patch.dict(os.environ, {"DATABASE_URL": postgres_url}),
        mock.patch.object(database, "create_engine"),
        mock.patch(
            "shared.database.create_database_if_not_exists"
        ) as bootstrap,
        mock.patch("psycopg2.connect"),
    ):
        reloaded = importlib.reload(database)

        database_url = cast("str", reloaded.SQLALCHEMY_DATABASE_URL)

        assert database_url == postgres_url

    _ = bootstrap
    _ = importlib.reload(database)


def test_the_refresh_cookie_is_secure_by_default() -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        os.environ["JWT_SECRET_KEY"] = "unit-test-secret-key-value"

        reloaded = importlib.reload(cookie_security)

        is_secure = cast("bool", reloaded.REFRESH_COOKIE_SECURE)

        assert is_secure is True

    _ = importlib.reload(cookie_security)


def test_the_refresh_cookie_can_be_made_insecure_for_local_http() -> None:
    with mock.patch.dict(
        os.environ, {"REFRESH_COOKIE_SECURE": "false"}
    ):
        reloaded = importlib.reload(cookie_security)

        is_secure = cast("bool", reloaded.REFRESH_COOKIE_SECURE)

        assert is_secure is False

    _ = importlib.reload(cookie_security)


def test_an_unreadable_refresh_cookie_setting_stops_the_service() -> None:
    with (
        mock.patch.dict(os.environ, {"REFRESH_COOKIE_SECURE": "maybe"}),
        pytest.raises(RuntimeError, match="REFRESH_COOKIE_SECURE"),
    ):
        _ = importlib.reload(cookie_security)

    _ = importlib.reload(cookie_security)


@given(
    spelling=strategies.sampled_from(
        ["1", "true", "yes", "on", "0", "false", "no", "off"]
    ),
    surrounding_space=strategies.text(alphabet=" \t", max_size=3),
)
def test_refresh_cookie_secure_property_reads_every_accepted_spelling(
    spelling: str, surrounding_space: str
) -> None:
    written_value = surrounding_space + spelling.upper() + surrounding_space

    with mock.patch.dict(
        os.environ, {"REFRESH_COOKIE_SECURE": written_value}
    ):
        reloaded = importlib.reload(cookie_security)

        is_secure = cast("bool", reloaded.REFRESH_COOKIE_SECURE)
        expected = spelling in {"1", "true", "yes", "on"}

        assert is_secure is expected

    _ = importlib.reload(cookie_security)
