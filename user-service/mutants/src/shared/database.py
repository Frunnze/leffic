import os
from collections.abc import Generator

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

db_name = "users"
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5455")
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)
_POSTGRES_SCHEME = "postgresql"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_create_database_if_not_exists__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_create_database_if_not_exists__mutmut)
def create_database_if_not_exists() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_orig() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_1() -> None:
    with psycopg2.connect(
        dbname=None,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_2() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=None,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_3() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=None,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_4() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=None,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_5() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=None,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_6() -> None:
    with psycopg2.connect(
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_7() -> None:
    with psycopg2.connect(
        dbname="postgres",
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_8() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_9() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_10() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_11() -> None:
    with psycopg2.connect(
        dbname="XXpostgresXX",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_12() -> None:
    with psycopg2.connect(
        dbname="POSTGRES",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def x_create_database_if_not_exists__mutmut_13() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(None)

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


def x_create_database_if_not_exists__mutmut_14() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                None, (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_15() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", None
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_16() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_17() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_18() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "XXSELECT 1 FROM pg_database WHERE datname = %sXX", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_19() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "select 1 from pg_database where datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_20() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM PG_DATABASE WHERE DATNAME = %S", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_21() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is not None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_22() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    None
                )


def x_create_database_if_not_exists__mutmut_23() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        None
                    )
                )


def x_create_database_if_not_exists__mutmut_24() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL(None).format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_25() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("XXCREATE DATABASE {}XX").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_26() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("create database {}").format(
                        sql.Identifier(db_name)
                    )
                )


def x_create_database_if_not_exists__mutmut_27() -> None:
    with psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    ) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(None)
                    )
                )

mutants_x_create_database_if_not_exists__mutmut['_mutmut_orig'] = x_create_database_if_not_exists__mutmut_orig # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_1'] = x_create_database_if_not_exists__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_2'] = x_create_database_if_not_exists__mutmut_2 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_3'] = x_create_database_if_not_exists__mutmut_3 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_4'] = x_create_database_if_not_exists__mutmut_4 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_5'] = x_create_database_if_not_exists__mutmut_5 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_6'] = x_create_database_if_not_exists__mutmut_6 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_7'] = x_create_database_if_not_exists__mutmut_7 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_8'] = x_create_database_if_not_exists__mutmut_8 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_9'] = x_create_database_if_not_exists__mutmut_9 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_10'] = x_create_database_if_not_exists__mutmut_10 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_11'] = x_create_database_if_not_exists__mutmut_11 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_12'] = x_create_database_if_not_exists__mutmut_12 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_13'] = x_create_database_if_not_exists__mutmut_13 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_14'] = x_create_database_if_not_exists__mutmut_14 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_15'] = x_create_database_if_not_exists__mutmut_15 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_16'] = x_create_database_if_not_exists__mutmut_16 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_17'] = x_create_database_if_not_exists__mutmut_17 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_18'] = x_create_database_if_not_exists__mutmut_18 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_19'] = x_create_database_if_not_exists__mutmut_19 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_20'] = x_create_database_if_not_exists__mutmut_20 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_21'] = x_create_database_if_not_exists__mutmut_21 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_22'] = x_create_database_if_not_exists__mutmut_22 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_23'] = x_create_database_if_not_exists__mutmut_23 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_24'] = x_create_database_if_not_exists__mutmut_24 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_25'] = x_create_database_if_not_exists__mutmut_25 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_26'] = x_create_database_if_not_exists__mutmut_26 # type: ignore # mutmut generated
mutants_x_create_database_if_not_exists__mutmut['x_create_database_if_not_exists__mutmut_27'] = x_create_database_if_not_exists__mutmut_27 # type: ignore # mutmut generated


if SQLALCHEMY_DATABASE_URL.startswith(_POSTGRES_SCHEME):
    create_database_if_not_exists()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
mutants_x_get_db__mutmut: MutantDict = {}  # type: ignore



@_mutmut_mutated(mutants_x_get_db__mutmut)
def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def x_get_db__mutmut_orig() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def x_get_db__mutmut_1() -> Generator[Session]:
    db = None
    try:
        yield db
    finally:
        db.close()

mutants_x_get_db__mutmut['_mutmut_orig'] = x_get_db__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_db__mutmut['x_get_db__mutmut_1'] = x_get_db__mutmut_1 # type: ignore # mutmut generated
