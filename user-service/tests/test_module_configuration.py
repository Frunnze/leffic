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
