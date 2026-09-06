import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from shared.models import Folder
from tests.folder_owner_support import (
    FOREIGN_HOME_ID,
    HOME_ID,
    added_folder,
)
from tests.support import foreign_key_enforcing_sessions, in_memory_sessions

_PRAGMA_FOREIGN_KEYS = text("PRAGMA foreign_keys")
_KEYS_ENFORCED = 1
_KEYS_IGNORED = 0


@pytest.fixture
def enforced() -> sessionmaker[Session]:
    return foreign_key_enforcing_sessions()


def test_the_foreign_key_factory_enforces_keys(
    enforced: sessionmaker[Session],
) -> None:
    with enforced() as session:
        assert (
            session.execute(_PRAGMA_FOREIGN_KEYS).scalar_one()
            == _KEYS_ENFORCED
        )


def test_in_memory_sessions_still_does_not_enforce_keys() -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        assert (
            session.execute(_PRAGMA_FOREIGN_KEYS).scalar_one()
            == _KEYS_IGNORED
        )


def test_a_cross_owner_child_is_rejected_by_the_database(
    enforced: sessionmaker[Session],
) -> None:
    with enforced() as session:
        parent_id = added_folder(session, HOME_ID, None, "mine")

    with enforced() as session, pytest.raises(IntegrityError):
        _ = added_folder(session, FOREIGN_HOME_ID, parent_id, "theirs")


def test_a_root_folder_still_inserts(
    enforced: sessionmaker[Session],
) -> None:
    with enforced() as session:
        root_id = added_folder(session, HOME_ID, None, "root")

    with enforced() as session:
        assert session.query(Folder).filter_by(id=root_id).count() == 1


def test_a_same_owner_child_still_inserts(
    enforced: sessionmaker[Session],
) -> None:
    with enforced() as session:
        parent_id = added_folder(session, HOME_ID, None, "parent")
        child_id = added_folder(session, HOME_ID, parent_id, "child")

    with enforced() as session:
        assert session.query(Folder).filter_by(id=child_id).count() == 1


def test_the_cascade_delete_still_works_with_keys_on(
    enforced: sessionmaker[Session],
) -> None:
    with enforced() as session:
        parent_id = added_folder(session, HOME_ID, None, "parent")
        child_id = added_folder(session, HOME_ID, parent_id, "child")

    with enforced() as session:
        parent = session.query(Folder).filter_by(id=parent_id).one()
        session.delete(parent)
        session.commit()

    with enforced() as session:
        assert session.query(Folder).filter_by(id=child_id).count() == 0
