from typing import cast

from sqlalchemy import ForeignKeyConstraint, Table, UniqueConstraint
from sqlalchemy.orm import configure_mappers

from shared.models import Folder

_OWNER_UNIQUENESS = "one_owner_per_folder"
_COMPOSITE_PARENT_KEY = "subfolder_shares_the_owner"
_OWNER_COLUMNS = ["id", "user_id"]
_COMPOSITE_COLUMNS = ["parent_id", "user_id"]
_COMPOSITE_TARGETS = ["folders.id", "folders.user_id"]
_ALL_WITH_ORPHANS = {
    "save-update",
    "merge",
    "refresh-expire",
    "expunge",
    "delete",
    "delete-orphan",
}
_FOLDERS: Table = Folder.metadata.tables["folders"]

type ColumnConstraint = UniqueConstraint | ForeignKeyConstraint


def _constraints_named(name: str) -> list[ColumnConstraint]:
    found: list[ColumnConstraint] = []

    for constraint in _FOLDERS.constraints:
        carries_columns = isinstance(
            constraint, UniqueConstraint | ForeignKeyConstraint
        )

        if carries_columns and constraint.name == name:
            found.append(constraint)

    return found


def _column_names(constraint: ColumnConstraint) -> list[str]:
    names: list[str] = []

    for column in constraint.columns:
        names.append(column.name)

    return names


def _foreign_key_targets(constraint: ForeignKeyConstraint) -> list[str]:
    targets: list[str] = []

    for element in constraint.elements:
        targets.append(cast("str", element.target_fullname))

    return targets


def _single_column_parent_keys() -> list[ForeignKeyConstraint]:
    found: list[ForeignKeyConstraint] = []

    for constraint in _FOLDERS.foreign_key_constraints:
        if _column_names(constraint) == ["parent_id"]:
            found.append(constraint)

    return found


def _relationship_columns(relationship_name: str) -> set[str]:
    relation = Folder.__mapper__.relationships[relationship_name]
    columns: set[str] = set()

    for local, remote in relation.local_remote_pairs or []:
        columns.add(cast("str", local.name))
        columns.add(cast("str", remote.name))

    return columns


def test_the_model_declares_the_owner_uniqueness() -> None:
    found = _constraints_named(_OWNER_UNIQUENESS)

    assert len(found) == 1
    assert isinstance(found[0], UniqueConstraint)
    assert _column_names(found[0]) == _OWNER_COLUMNS


def test_the_model_declares_the_composite_parent_key() -> None:
    found = _constraints_named(_COMPOSITE_PARENT_KEY)

    assert len(found) == 1
    assert isinstance(found[0], ForeignKeyConstraint)
    assert _column_names(found[0]) == _COMPOSITE_COLUMNS
    assert _foreign_key_targets(found[0]) == _COMPOSITE_TARGETS


def test_parent_id_keeps_its_single_column_foreign_key() -> None:
    found = _single_column_parent_keys()

    assert len(found) == 1
    assert _foreign_key_targets(found[0]) == ["folders.id"]


def test_the_folder_mappers_configure() -> None:
    configure_mappers()

    assert _relationship_columns("folder") == {"id", "parent_id"}
    assert _relationship_columns("subfolders") == {"id", "parent_id"}


def test_the_subfolder_cascade_is_unchanged() -> None:
    cascade = Folder.__mapper__.relationships["subfolders"].cascade

    assert set(cascade) == _ALL_WITH_ORPHANS

