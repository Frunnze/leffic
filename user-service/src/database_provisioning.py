from contextlib import closing

import psycopg2
from psycopg2 import sql

from shared.database_settings import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
    POSTGRES_SCHEME,
)

_ADMINISTRATIVE_DATABASE = "postgres"


def create_database_if_not_exists() -> None:
    with closing(
        psycopg2.connect(
            dbname=_ADMINISTRATIVE_DATABASE,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
        )
    ) as connection:
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (DATABASE_NAME,),
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(DATABASE_NAME)
                    )
                )


def create_postgres_database_if_configured(database_url: str) -> None:
    if not database_url.startswith(POSTGRES_SCHEME):
        return

    create_database_if_not_exists()
