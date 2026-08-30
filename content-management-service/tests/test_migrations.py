from pathlib import Path
from unittest import mock

import pytest
from alembic.command import downgrade, upgrade
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from shared.database import Base
from tests.migration_environment_support import (
    call_lines_in_function,
    module_scope_bootstrap_call_count,
    module_scope_url_fallback_is_present,
    names_imported_from_the_database_module,
)
from tests.migration_support import alembic_config


@pytest.fixture
def migrated_database(tmp_path: Path) -> str:
    database_url = f"sqlite:///{tmp_path / 'migrated.db'}"
    upgrade(alembic_config(database_url), "head")

    return database_url


def test_migrations_have_a_single_head() -> None:
    scripts = ScriptDirectory.from_config(alembic_config("sqlite://"))

    assert len(scripts.get_heads()) == 1


def test_every_model_table_is_created_by_the_migrations(
    migrated_database: str,
) -> None:
    engine = create_engine(migrated_database)
    migrated_tables = set(inspect(engine).get_table_names())

    assert set(Base.metadata.tables) <= migrated_tables


def test_migrations_create_no_table_the_models_do_not_declare(
    migrated_database: str,
) -> None:
    engine = create_engine(migrated_database)
    migrated_tables = set(inspect(engine).get_table_names())
    declared = set(Base.metadata.tables) | {"alembic_version"}

    assert migrated_tables <= declared


def test_every_model_column_is_created_by_the_migrations(
    migrated_database: str,
) -> None:
    engine = create_engine(migrated_database)
    inspector = inspect(engine)

    for table_name, table in Base.metadata.tables.items():
        migrated_columns = {
            column["name"] for column in inspector.get_columns(table_name)
        }

        assert set(table.columns.keys()) == migrated_columns, table_name


def test_downgrade_removes_every_model_table(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'reversible.db'}"
    config = alembic_config(database_url)
    upgrade(config, "head")
    downgrade(config, "base")
    engine = create_engine(database_url)
    remaining = set(inspect(engine).get_table_names())

    assert remaining & set(Base.metadata.tables) == set()


_BOOTSTRAP_NAME = "create_postgres_database_if_configured"
_ENGINE_FACTORY_NAME = "engine_from_config"
_ONLINE_FUNCTION = "run_migrations_online"
_OFFLINE_FUNCTION = "run_migrations_offline"
_PSYCOPG2_CONNECT_TARGET = "psycopg2.connect"
_MODULE_URL_ATTRIBUTE = "shared.database.SQLALCHEMY_DATABASE_URL"
_POSTGRES_MODULE_URL = (
    "postgresql://postgres:postgres@localhost:5455/content"
)


def test_the_migration_environment_imports_the_postgres_bootstrap() -> None:
    imported = names_imported_from_the_database_module()

    assert _BOOTSTRAP_NAME in imported
    assert "SQLALCHEMY_DATABASE_URL" in imported
    assert "Base" in imported


def test_the_migration_environment_never_bootstraps_at_module_scope(
) -> None:
    assert module_scope_bootstrap_call_count() == 0


def test_the_online_migration_run_bootstraps_exactly_once() -> None:
    bootstrap_lines = call_lines_in_function(
        _ONLINE_FUNCTION, _BOOTSTRAP_NAME
    )

    assert len(bootstrap_lines) == 1


def test_the_online_bootstrap_runs_before_the_engine_is_built() -> None:
    bootstrap_lines = call_lines_in_function(
        _ONLINE_FUNCTION, _BOOTSTRAP_NAME
    )
    engine_lines = call_lines_in_function(
        _ONLINE_FUNCTION, _ENGINE_FACTORY_NAME
    )

    assert bootstrap_lines[0] < engine_lines[0]


def test_the_offline_migration_run_never_bootstraps() -> None:
    bootstrap_lines = call_lines_in_function(
        _OFFLINE_FUNCTION, _BOOTSTRAP_NAME
    )

    assert bootstrap_lines == []


def test_the_migration_environment_keeps_the_configured_url_fallback(
) -> None:
    assert module_scope_url_fallback_is_present()


def test_a_sqlite_upgrade_opens_no_postgres_connection(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'guarded.db'}"

    with mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect:
        upgrade(alembic_config(database_url), "head")

    assert connect.call_count == 0


def test_a_sqlite_downgrade_opens_no_postgres_connection(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'guarded_down.db'}"
    config = alembic_config(database_url)
    upgrade(config, "head")

    with mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect:
        downgrade(config, "base")

    assert connect.call_count == 0


def test_an_offline_sqlite_upgrade_opens_no_postgres_connection(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'offline.db'}"

    with mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect:
        upgrade(alembic_config(database_url), "head", sql=True)

    assert connect.call_count == 0


def test_an_online_sqlite_upgrade_ignores_a_postgres_module_url(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'online_module.db'}"

    with (
        mock.patch(_MODULE_URL_ATTRIBUTE, _POSTGRES_MODULE_URL),
        mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect,
    ):
        upgrade(alembic_config(database_url), "head")

    assert connect.call_count == 0


def test_an_offline_sqlite_upgrade_ignores_a_postgres_module_url(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'offline_module.db'}"

    with (
        mock.patch(_MODULE_URL_ATTRIBUTE, _POSTGRES_MODULE_URL),
        mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect,
    ):
        upgrade(alembic_config(database_url), "head", sql=True)

    assert connect.call_count == 0
