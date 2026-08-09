import os
from collections.abc import Generator
from contextlib import closing

import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

db_name = "content"
db_user = os.getenv("CM_DB_USER", "postgres")
db_pass = os.getenv("CM_DB_PASS", "postgres")
db_host = os.getenv("CM_DB_HOST", "localhost")
db_port = os.getenv("CM_DB_PORT", "5455")
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)
_POSTGRES_SCHEME = "postgresql"


def create_database_if_not_exists() -> None:
    with closing(
        psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
        )
    ) as connection:
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


if SQLALCHEMY_DATABASE_URL.startswith(_POSTGRES_SCHEME):
    create_database_if_not_exists()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass



def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
