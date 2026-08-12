import uuid

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.file_system.folder_contents import entries_in
from shared.models import Folder, Note
from tests.access_support import HOME_ID, OTHER_HOME_ID
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.add(
            Folder(id=OTHER_HOME_ID, name="Home", user_id=OTHER_HOME_ID)
        )
        session.commit()

    return factory


def _noted_folder(
    session: Session, owner: uuid.UUID, note_name: str
) -> Folder:
    folder = Folder(name="Shelf", user_id=owner)
    session.add(folder)
    session.commit()
    session.add(
        Note(
            folder_id=folder.id,
            name=note_name,
            content="body",
            type="general",
        )
    )
    session.commit()

    return folder


def test_notes_of_another_owner_are_not_returned(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        theirs = _noted_folder(session, OTHER_HOME_ID, "Confidential")

        assert entries_in(session, str(theirs.id), USER_ID) == []


def test_notes_of_the_owner_are_returned(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        theirs = _noted_folder(session, OTHER_HOME_ID, "Confidential")
        entries = entries_in(session, str(theirs.id), OTHER_USER_ID)

        assert [entry["name"] for entry in entries] == ["Confidential"]


def test_notes_of_another_folder_are_not_returned(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        listed = _noted_folder(session, HOME_ID, "Here")
        _ = _noted_folder(session, HOME_ID, "Away")
        entries = entries_in(session, str(listed.id), USER_ID)

        assert [entry["name"] for entry in entries] == ["Here"]
