import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import aliased

from shared.models import Folder


def subfolder_ids(
    folder_id: str, user_id: str
) -> Select[tuple[uuid.UUID]]:
    folder_cte = (
        select(Folder.id)
        .where(Folder.id == folder_id, Folder.user_id == user_id)
        .cte(recursive=True)
    )
    subfolder = aliased(Folder)
    recursive_cte = folder_cte.union_all(
        select(subfolder.id).where(
            subfolder.parent_id == folder_cte.c.id,
            subfolder.user_id == user_id,
        )
    )

    return select(recursive_cte.c.id)
