import uuid
from unittest import mock

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.user_events import user_cleanup
from features.user_events.user_cleanup import remove_everything_owned_by
from shared.models import File, FlashcardDeck, Folder, Note
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions

HOME_ID = uuid.UUID(USER_ID)
OTHER_HOME_ID = uuid.UUID(OTHER_USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _populated(session: Session, owner: uuid.UUID) -> None:
    session.add(Folder(id=owner, name="Home", user_id=owner))
    session.commit()
    session.add_all(
        [
            FlashcardDeck(name="Deck", folder_id=owner),
            Note(name="Note", folder_id=owner, type="general", content="hi"),
            File(name="notes.pdf", folder_id=owner, extension="pdf"),
        ]
    )
    session.commit()


def test_every_folder_of_the_user_is_removed(
    sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _populated(session, HOME_ID)

    with sessions() as session, mock.patch.object(
        user_cleanup, "delete_file_from_storage"
    ):
        removed = remove_everything_owned_by(session, USER_ID)

    with sessions() as session:
        assert removed == 1
        assert session.query(Folder).all() == []
        assert session.query(FlashcardDeck).all() == []
        assert session.query(Note).all() == []


def test_another_users_content_is_left_alone(
    sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _populated(session, HOME_ID)
        _populated(session, OTHER_HOME_ID)

    with sessions() as session, mock.patch.object(
        user_cleanup, "delete_file_from_storage"
    ):
        _ = remove_everything_owned_by(session, USER_ID)

    with sessions() as session:
        remaining = session.query(Folder).all()

        assert len(remaining) == 1
        assert remaining[0].user_id == OTHER_HOME_ID
        assert len(session.query(Note).all()) == 1


def test_the_stored_files_are_deleted_too(
    sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _populated(session, HOME_ID)
        stored = session.query(File).one()
        expected_name = f"{stored.id}.pdf"

    with sessions() as session, mock.patch.object(
        user_cleanup, "delete_file_from_storage"
    ) as remove_file:
        _ = remove_everything_owned_by(session, USER_ID)

    assert remove_file.call_args.args[0] == expected_name


def test_a_user_without_content_removes_nothing(
    sessions: sessionmaker[Session]
) -> None:
    with sessions() as session, mock.patch.object(
        user_cleanup, "delete_file_from_storage"
    ) as remove_file:
        removed = remove_everything_owned_by(session, USER_ID)

    assert removed == 0
    assert remove_file.call_args is None

