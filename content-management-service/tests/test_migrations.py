from pathlib import Path

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from shared.database import Base

_ALEMBIC_INI_NAME = "alembic.ini"
_MISSING_ALEMBIC_INI = "No alembic.ini above this test file"


def _service_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / _ALEMBIC_INI_NAME).is_file():
            return candidate

    raise RuntimeError(_MISSING_ALEMBIC_INI)


def _alembic_config(database_url: str) -> Config:
    root = _service_root()
    config = Config(str(root / _ALEMBIC_INI_NAME))
    config.set_main_option("script_location", str(root / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)

    return config


@pytest.fixture
def migrated_database(tmp_path: Path) -> str:
    database_url = f"sqlite:///{tmp_path / 'migrated.db'}"
    upgrade(_alembic_config(database_url), "head")

    return database_url


def test_migrations_have_a_single_head() -> None:
    scripts = ScriptDirectory.from_config(_alembic_config("sqlite://"))

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
    config = _alembic_config(database_url)
    upgrade(config, "head")
    downgrade(config, "base")
    engine = create_engine(database_url)
    remaining = set(inspect(engine).get_table_names())

    assert remaining & set(Base.metadata.tables) == set()
