import pytest
from alembic.command import downgrade, upgrade
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import Engine

from tests.folder_migration_support import (
    OWNER_ONE,
    OWNER_THREE,
    OWNER_TWO,
    FolderRow,
    database_at_the_session_revision,
    folder_row,
    foreign_key_columns,
    parent_of,
    seeded_folders,
    unique_constraint_names,
)
from tests.migration_support import SESSION_REVISION

type ConstraintShape = tuple[set[str | None], list[list[str]]]

_OWNERS = (OWNER_ONE, OWNER_TWO, OWNER_THREE)
_OWNER_CHAINS = st.lists(
    st.integers(min_value=0, max_value=len(_OWNERS) - 1),
    min_size=1,
    max_size=5,
)
_MIGRATION_SETTINGS = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def _chain_rows(owner_indexes: list[int]) -> list[FolderRow]:
    rows: list[FolderRow] = []

    for owner_index in owner_indexes:
        parent_id = rows[-1].folder_id if rows else None
        rows.append(folder_row(_OWNERS[owner_index], parent_id))

    return rows


def _owners_by_folder(rows: list[FolderRow]) -> dict[str, str]:
    owners: dict[str, str] = {}

    for row in rows:
        owners[row.folder_id.hex] = row.owner.hex

    return owners


def _constraint_shape(engine: Engine) -> ConstraintShape:
    return unique_constraint_names(engine), sorted(
        foreign_key_columns(engine)
    )


@_MIGRATION_SETTINGS
@given(_OWNER_CHAINS)
def test_upgrade_property_leaves_no_cross_owner_edge_behind(
    tmp_path_factory: pytest.TempPathFactory, owner_indexes: list[int]
) -> None:
    config, engine = database_at_the_session_revision(
        tmp_path_factory.mktemp("quarantined")
    )
    rows = _chain_rows(owner_indexes)
    seeded_folders(engine, rows)
    owners = _owners_by_folder(rows)

    upgrade(config, "head")

    for row in rows:
        parent = parent_of(engine, row.folder_id)

        assert parent is None or owners[parent] == row.owner.hex


@_MIGRATION_SETTINGS
@given(_OWNER_CHAINS)
def test_downgrade_property_restores_the_session_revision_shape(
    tmp_path_factory: pytest.TempPathFactory, owner_indexes: list[int]
) -> None:
    config, engine = database_at_the_session_revision(
        tmp_path_factory.mktemp("round-tripped")
    )
    seeded_folders(engine, _chain_rows(owner_indexes))
    before = _constraint_shape(engine)

    upgrade(config, "head")
    downgrade(config, SESSION_REVISION)

    assert _constraint_shape(engine) == before
