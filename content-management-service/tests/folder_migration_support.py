import uuid
from pathlib import Path
from typing import NamedTuple, cast

from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import (
    Engine,
    column,
    create_engine,
    func,
    inspect,
    select,
    table,
)

from tests.migration_support import SESSION_REVISION, alembic_config

OWNER_ONE = uuid.UUID("6f1c7d4e-0000-4000-8000-00000000aa01")
OWNER_TWO = uuid.UUID("6f1c7d4e-0000-4000-8000-00000000aa02")
OWNER_THREE = uuid.UUID("6f1c7d4e-0000-4000-8000-00000000aa03")

OWNER_UNIQUENESS = "one_owner_per_folder"
COMPOSITE_PARENT_COLUMNS = ["parent_id", "user_id"]
OWNER_UNIQUENESS_COLUMNS = ["id", "user_id"]

_FOLDERS_TABLE = "folders"
_DATABASE_NAME = "folders.db"
_SEEDED_TIMESTAMP = "2026-01-01 00:00:00"
_FOLDERS = table(
    _FOLDERS_TABLE,
    column("id"),
    column("parent_id"),
    column("user_id"),
    column("name"),
    column("created_at"),
    column("public"),
)


class FolderRow(NamedTuple):
    folder_id: uuid.UUID
    owner: uuid.UUID
    parent_id: uuid.UUID | None


def folder_row(
    owner: uuid.UUID, parent_id: uuid.UUID | None = None
) -> FolderRow:
    return FolderRow(
        folder_id=uuid.uuid4(), owner=owner, parent_id=parent_id
    )


def database_url(directory: Path) -> str:
    return f"sqlite:///{directory / _DATABASE_NAME}"


def database_at_the_session_revision(
    directory: Path,
) -> tuple[Config, Engine]:
    url = database_url(directory)
    config = alembic_config(url)
    upgrade(config, SESSION_REVISION)

    return config, create_engine(url)


def database_at_head(directory: Path) -> Engine:
    url = database_url(directory)
    upgrade(alembic_config(url), "head")

    return create_engine(url)


def seeded_folders(engine: Engine, rows: list[FolderRow]) -> None:
    with engine.begin() as connection:
        for row in rows:
            parent = None if row.parent_id is None else row.parent_id.hex
            _ = connection.execute(
                _FOLDERS.insert().values(
                    id=row.folder_id.hex,
                    parent_id=parent,
                    user_id=row.owner.hex,
                    name=f"folder-{row.folder_id.hex[:6]}",
                    created_at=_SEEDED_TIMESTAMP,
                    public=False,
                )
            )


def parent_of(engine: Engine, folder_id: uuid.UUID) -> str | None:
    wanted = select(_FOLDERS.c.parent_id).where(
        _FOLDERS.c.id == folder_id.hex
    )

    with engine.connect() as connection:
        return cast("str | None", connection.execute(wanted).scalar_one())


def folder_count(engine: Engine) -> int:
    counted = select(func.count()).select_from(_FOLDERS)

    with engine.connect() as connection:
        return connection.execute(counted).scalar_one()


def unique_constraint_names(engine: Engine) -> set[str | None]:
    names: set[str | None] = set()
    constraints = inspect(engine).get_unique_constraints(_FOLDERS_TABLE)

    for constraint in constraints:
        names.add(constraint["name"])

    return names


def unique_constraint_columns(engine: Engine, name: str) -> list[list[str]]:
    columns: list[list[str]] = []
    constraints = inspect(engine).get_unique_constraints(_FOLDERS_TABLE)

    for constraint in constraints:
        if constraint["name"] == name:
            columns.append(list(constraint["column_names"]))

    return columns


def foreign_key_columns(engine: Engine) -> list[list[str]]:
    columns: list[list[str]] = []

    for key in inspect(engine).get_foreign_keys(_FOLDERS_TABLE):
        columns.append(list(key["constrained_columns"]))

    return columns


def foreign_key_targets(
    engine: Engine, constrained_columns: list[str]
) -> list[tuple[str, list[str]]]:
    targets: list[tuple[str, list[str]]] = []

    for key in inspect(engine).get_foreign_keys(_FOLDERS_TABLE):
        if list(key["constrained_columns"]) == constrained_columns:
            targets.append(
                (key["referred_table"], list(key["referred_columns"]))
            )

    return targets


def index_columns(engine: Engine) -> list[list[str | None]]:
    columns: list[list[str | None]] = []

    for index in inspect(engine).get_indexes(_FOLDERS_TABLE):
        columns.append(list(index["column_names"]))

    return columns
