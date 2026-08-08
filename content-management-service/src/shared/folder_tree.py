import uuid

from sqlalchemy import ColumnElement, Select, select
from sqlalchemy.orm import aliased

from src.shared.models import Folder

_SUBFOLDERS_CTE = "subfolders"


def subfolder_ids(
    folder_id: str, user_id: str | None = None
) -> Select[tuple[uuid.UUID]]:
    conditions: list[ColumnElement[bool]] = [Folder.id == folder_id]

    if user_id is not None:
        conditions.append(Folder.user_id == user_id)

    folder_cte = (
        select(Folder.id)
        .where(*conditions)
        .cte(name=_SUBFOLDERS_CTE, recursive=True)
    )
    subfolder = aliased(Folder)
    recursive_cte = folder_cte.union_all(
        select(subfolder.id).where(subfolder.parent_id == folder_cte.c.id)
    )

    return select(recursive_cte.c.id)
