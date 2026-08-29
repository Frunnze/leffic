import ast
from pathlib import Path
from unittest import mock

import pytest
from alembic.command import downgrade, upgrade
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from shared.database import Base
from tests.migration_support import alembic_config, service_root


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
_DATABASE_MODULE = "shared.database"
_OFFLINE_DISPATCH = "is_offline_mode"
_PSYCOPG2_CONNECT_TARGET = "psycopg2.connect"
_MISSING_DISPATCH = "env.py has no offline-mode dispatch"


def _environment_tree() -> ast.Module:
    source = (service_root() / "migrations" / "env.py").read_text(
        encoding="utf-8"
    )

    return ast.parse(source)


def _names_imported_from_the_database_module() -> set[str]:
    imported: set[str] = set()

    for node in ast.walk(_environment_tree()):
        if not isinstance(node, ast.ImportFrom):
            continue

        if node.module != _DATABASE_MODULE:
            continue

        for alias in node.names:
            imported.add(alias.name)

    return imported


def _module_scope_bootstrap_calls() -> list[ast.Call]:
    calls: list[ast.Call] = []

    for node in _environment_tree().body:
        if not isinstance(node, ast.Expr):
            continue

        called = node.value

        if not isinstance(called, ast.Call):
            continue

        is_bootstrap_call = (
            isinstance(called.func, ast.Name)
            and called.func.id == _BOOTSTRAP_NAME
        )

        if is_bootstrap_call:
            calls.append(called)

    return calls


def _offline_dispatch_line() -> int:
    for node in _environment_tree().body:
        if not isinstance(node, ast.If):
            continue

        dispatch_test = node.test

        if not isinstance(dispatch_test, ast.Call):
            continue

        dispatched = dispatch_test.func

        if (
            isinstance(dispatched, ast.Attribute)
            and dispatched.attr == _OFFLINE_DISPATCH
        ):
            return node.lineno

    raise AssertionError(_MISSING_DISPATCH)


def test_the_migration_environment_imports_the_postgres_bootstrap() -> None:
    imported = _names_imported_from_the_database_module()

    assert _BOOTSTRAP_NAME in imported
    assert "SQLALCHEMY_DATABASE_URL" in imported
    assert "Base" in imported


def test_the_migration_environment_calls_the_bootstrap_at_module_scope(
) -> None:
    assert len(_module_scope_bootstrap_calls()) == 1


def test_the_bootstrap_runs_before_the_offline_mode_dispatch() -> None:
    call = _module_scope_bootstrap_calls()[0]

    assert call.lineno < _offline_dispatch_line()


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
