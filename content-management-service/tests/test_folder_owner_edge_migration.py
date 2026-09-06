import uuid
from pathlib import Path
from unittest import mock

from alembic.command import downgrade, upgrade
from alembic.script import ScriptDirectory

from tests.folder_migration_support import (
    COMPOSITE_PARENT_COLUMNS,
    OWNER_ONE,
    OWNER_THREE,
    OWNER_TWO,
    OWNER_UNIQUENESS,
    OWNER_UNIQUENESS_COLUMNS,
    FolderRow,
    database_at_head,
    database_at_the_session_revision,
    database_url,
    folder_count,
    folder_row,
    foreign_key_columns,
    foreign_key_targets,
    index_columns,
    parent_of,
    seeded_folders,
    unique_constraint_columns,
    unique_constraint_names,
)
from tests.migration_support import SESSION_REVISION, alembic_config

_PSYCOPG2_CONNECT_TARGET = "psycopg2.connect"
_PARENT_INDEX_COLUMNS = [["parent_id"]]
_SEEDED_ROW_COUNT = 4


def test_the_new_revision_is_the_single_head() -> None:
    scripts = ScriptDirectory.from_config(alembic_config("sqlite://"))
    heads = scripts.get_heads()

    assert len(heads) == 1
    assert scripts.get_revision(heads[0]).down_revision == SESSION_REVISION


def test_a_cross_owner_edge_is_quarantined(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    parent = folder_row(OWNER_ONE)
    child = folder_row(OWNER_TWO, parent.folder_id)
    seeded_folders(engine, [parent, child])

    upgrade(config, "head")

    assert parent_of(engine, child.folder_id) is None


def test_a_three_owner_chain_is_fully_quarantined(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    top = folder_row(OWNER_ONE)
    middle = folder_row(OWNER_TWO, top.folder_id)
    leaf = folder_row(OWNER_THREE, middle.folder_id)
    seeded_folders(engine, [top, middle, leaf])

    upgrade(config, "head")

    assert parent_of(engine, middle.folder_id) is None
    assert parent_of(engine, leaf.folder_id) is None


def test_a_dangling_parent_id_is_quarantined(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    orphan = folder_row(OWNER_ONE, uuid.uuid4())
    seeded_folders(engine, [orphan])

    upgrade(config, "head")

    assert parent_of(engine, orphan.folder_id) is None


def test_a_self_parenting_folder_keeps_its_parent_id(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    folder_id = uuid.uuid4()
    looped = FolderRow(
        folder_id=folder_id, owner=OWNER_ONE, parent_id=folder_id
    )
    seeded_folders(engine, [looped])

    upgrade(config, "head")

    assert parent_of(engine, folder_id) == folder_id.hex


def test_same_owner_edges_survive_the_upgrade(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    parent = folder_row(OWNER_ONE)
    child = folder_row(OWNER_ONE, parent.folder_id)
    grandchild = folder_row(OWNER_ONE, child.folder_id)
    seeded_folders(engine, [parent, child, grandchild])

    upgrade(config, "head")

    assert parent_of(engine, child.folder_id) == parent.folder_id.hex
    assert parent_of(engine, grandchild.folder_id) == child.folder_id.hex


def test_the_upgrade_preserves_every_folder_row(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    parent = folder_row(OWNER_ONE)
    owned_child = folder_row(OWNER_ONE, parent.folder_id)
    foreign_child = folder_row(OWNER_TWO, parent.folder_id)
    orphan = folder_row(OWNER_THREE, uuid.uuid4())
    seeded_folders(engine, [parent, owned_child, foreign_child, orphan])

    upgrade(config, "head")

    assert folder_count(engine) == _SEEDED_ROW_COUNT


def test_the_upgrade_adds_the_owner_uniqueness(tmp_path: Path) -> None:
    engine = database_at_head(tmp_path)
    found = unique_constraint_columns(engine, OWNER_UNIQUENESS)

    assert found == [OWNER_UNIQUENESS_COLUMNS]


def test_the_upgrade_adds_the_composite_parent_key(tmp_path: Path) -> None:
    targets = foreign_key_targets(
        database_at_head(tmp_path), COMPOSITE_PARENT_COLUMNS
    )

    assert targets == [("folders", OWNER_UNIQUENESS_COLUMNS)]


def test_the_upgrade_adds_no_index(tmp_path: Path) -> None:
    assert index_columns(database_at_head(tmp_path)) == _PARENT_INDEX_COLUMNS


def test_the_downgrade_drops_both_constraints(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    upgrade(config, "head")

    assert OWNER_UNIQUENESS in unique_constraint_names(engine)
    assert COMPOSITE_PARENT_COLUMNS in foreign_key_columns(engine)

    downgrade(config, SESSION_REVISION)

    assert OWNER_UNIQUENESS not in unique_constraint_names(engine)
    assert COMPOSITE_PARENT_COLUMNS not in foreign_key_columns(engine)


def test_the_downgrade_leaves_the_quarantine_alone(tmp_path: Path) -> None:
    config, engine = database_at_the_session_revision(tmp_path)
    parent = folder_row(OWNER_ONE)
    child = folder_row(OWNER_TWO, parent.folder_id)
    seeded_folders(engine, [parent, child])

    upgrade(config, "head")
    downgrade(config, SESSION_REVISION)

    assert parent_of(engine, child.folder_id) is None


def test_the_folder_upgrade_opens_no_postgres_connection(
    tmp_path: Path,
) -> None:
    config = alembic_config(database_url(tmp_path))

    with mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect:
        upgrade(config, "head")

    assert connect.call_count == 0


def test_the_folder_downgrade_opens_no_postgres_connection(
    tmp_path: Path,
) -> None:
    config = alembic_config(database_url(tmp_path))
    upgrade(config, "head")

    with mock.patch(_PSYCOPG2_CONNECT_TARGET) as connect:
        downgrade(config, SESSION_REVISION)

    assert connect.call_count == 0
