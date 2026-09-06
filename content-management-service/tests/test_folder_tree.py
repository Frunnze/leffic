import inspect
import uuid
from typing import cast

from shared.folder_tree import subfolder_ids

_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"
_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_EXPECTED_PARAMETERS = ("folder_id", "user_id")


def _sql(folder_id: str, user_id: str) -> str:
    return " ".join(str(subfolder_ids(folder_id, user_id)).split())


def test_the_query_is_a_recursive_cte() -> None:
    assert _sql(_FOLDER_ID, _USER_ID).upper().startswith("WITH RECURSIVE")


def test_the_query_walks_from_parent_to_child() -> None:
    assert "folders_1.parent_id" in _sql(_FOLDER_ID, _USER_ID)


def test_subfolder_ids_requires_an_owner() -> None:
    parameters = inspect.signature(subfolder_ids).parameters
    owner = parameters["user_id"]

    assert tuple(parameters) == _EXPECTED_PARAMETERS
    assert cast("object", owner.default) is inspect.Parameter.empty
    assert cast("object", owner.annotation) is str
    assert cast("object", parameters["folder_id"].annotation) is str


def test_the_query_selects_one_column() -> None:
    query = subfolder_ids(str(uuid.UUID(_FOLDER_ID)), _USER_ID)

    assert len(query.selected_columns) == 1
    assert "folders.id" in _sql(_FOLDER_ID, _USER_ID)
