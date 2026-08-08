import uuid

from shared.folder_tree import subfolder_ids

_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"
_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"


def _sql(folder_id: str, user_id: str | None = None) -> str:
    return " ".join(str(subfolder_ids(folder_id, user_id)).split())


def test_the_query_is_a_recursive_cte() -> None:
    assert _sql(_FOLDER_ID).upper().startswith("WITH RECURSIVE")


def test_the_query_walks_from_parent_to_child() -> None:
    assert "folders_1.parent_id" in _sql(_FOLDER_ID)


def test_the_owner_is_only_required_when_given() -> None:
    assert "user_id" in _sql(_FOLDER_ID, _USER_ID)
    assert "user_id" not in _sql(_FOLDER_ID)


def test_the_query_selects_one_column() -> None:
    query = subfolder_ids(str(uuid.UUID(_FOLDER_ID)))

    assert len(query.selected_columns) == 1
    assert "folders.id" in _sql(_FOLDER_ID)
