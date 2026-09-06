import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from shared.folder_tree import subfolder_ids
from shared.models import Folder
from tests.support import OTHER_USER_ID, USER_ID

HOME_NAME = "Home"
HOME_ID = uuid.UUID(USER_ID)
FOREIGN_HOME_ID = uuid.UUID(OTHER_USER_ID)


def added_home(session: Session, owner: uuid.UUID) -> None:
    session.add(Folder(id=owner, name=HOME_NAME, user_id=owner))
    session.commit()


def added_folder(
    session: Session,
    owner: uuid.UUID,
    parent_id: uuid.UUID | None,
    name: str,
) -> uuid.UUID:
    folder = Folder(
        id=uuid.uuid4(), parent_id=parent_id, name=name, user_id=owner
    )
    session.add(folder)
    session.commit()

    return folder.id


def added_descendant_chain(
    session: Session,
    owner: uuid.UUID,
    parent_id: uuid.UUID,
    depth: int,
) -> list[uuid.UUID]:
    created: list[uuid.UUID] = []
    current_parent = parent_id

    for level in range(depth):
        current_parent = added_folder(
            session, owner, current_parent, f"level-{level}"
        )
        created.append(current_parent)

    return created


def added_ownership_chain(
    session: Session, ownership_flags: list[bool]
) -> uuid.UUID:
    root_id = added_folder(session, HOME_ID, None, "root")
    current_parent = root_id

    for depth, is_owned_by_caller in enumerate(ownership_flags):
        owner = HOME_ID if is_owned_by_caller else FOREIGN_HOME_ID
        current_parent = added_folder(
            session, owner, current_parent, f"node-{depth}"
        )

    return root_id


def returned_subtree(
    sessions: sessionmaker[Session], folder_id: uuid.UUID, owner: str
) -> set[uuid.UUID]:
    with sessions() as session:
        rows = session.execute(
            subfolder_ids(str(folder_id), owner)
        ).scalars().all()

    return set(rows)


def owners_of(
    session: Session, folder_ids: set[uuid.UUID]
) -> set[uuid.UUID]:
    rows = session.execute(
        select(Folder.user_id).where(Folder.id.in_(folder_ids))
    ).scalars().all()

    return set(rows)
