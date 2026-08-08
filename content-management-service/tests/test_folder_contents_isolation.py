import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.file_system.folder_contents import entries_in
from shared.models import (
    File,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions

_HOME_ID = uuid.UUID(USER_ID)
_OTHER_HOME_ID = uuid.UUID(OTHER_USER_ID)
_MADE_AT = datetime(2026, 8, 8, 17, 0, 0)  # noqa: DTZ001


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def _two_homes(session: Session) -> None:
    session.add(
        Folder(
            id=_HOME_ID, name="Home", user_id=_HOME_ID, created_at=_MADE_AT
        )
    )
    session.add(
        Folder(
            id=_OTHER_HOME_ID,
            name="Home",
            user_id=_OTHER_HOME_ID,
            created_at=_MADE_AT,
        )
    )
    session.commit()


def _entries(sessions: sessionmaker[Session]) -> list[dict[str, str]]:
    with sessions() as session:
        return entries_in(session, str(_HOME_ID), USER_ID)


def test_another_users_subfolder_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        session.add(
            Folder(
                parent_id=_HOME_ID,
                name="Theirs",
                user_id=_OTHER_HOME_ID,
                created_at=_MADE_AT,
            )
        )
        session.commit()

    assert _entries(sessions) == []


def test_another_users_deck_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        session.add(
            FlashcardDeck(
                folder_id=_OTHER_HOME_ID, name="Theirs", created_at=_MADE_AT
            )
        )
        session.commit()

    assert _entries(sessions) == []


def test_another_users_test_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        session.add(
            Test(
                folder_id=_OTHER_HOME_ID, name="Theirs", created_at=_MADE_AT
            )
        )
        session.commit()

    assert _entries(sessions) == []


def test_another_users_file_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        session.add(
            File(
                folder_id=_OTHER_HOME_ID,
                name="theirs",
                extension="pdf",
                created_at=_MADE_AT,
            )
        )
        session.commit()

    assert _entries(sessions) == []


def test_a_note_in_another_folder_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        session.add(
            Note(
                folder_id=_OTHER_HOME_ID,
                name="Theirs",
                content="body",
                type="general",
                created_at=_MADE_AT,
            )
        )
        session.commit()

    assert _entries(sessions) == []


def _second_folder(session: Session) -> uuid.UUID:
    elsewhere = Folder(
        parent_id=_HOME_ID,
        name="Elsewhere",
        user_id=_HOME_ID,
        created_at=_MADE_AT,
    )
    session.add(elsewhere)
    session.commit()

    return elsewhere.id


def test_a_deck_in_another_folder_of_mine_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        elsewhere = _second_folder(session)
        session.add(
            FlashcardDeck(
                folder_id=elsewhere, name="Deep", created_at=_MADE_AT
            )
        )
        session.commit()

    listed = _entries(sessions)

    assert [entry["type"] for entry in listed] == ["folder"]


def test_a_test_in_another_folder_of_mine_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        elsewhere = _second_folder(session)
        session.add(
            Test(folder_id=elsewhere, name="Deep", created_at=_MADE_AT)
        )
        session.commit()

    listed = _entries(sessions)

    assert [entry["type"] for entry in listed] == ["folder"]


def test_a_file_in_another_folder_of_mine_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _two_homes(session)
        elsewhere = _second_folder(session)
        session.add(
            File(
                folder_id=elsewhere,
                name="deep",
                extension="pdf",
                created_at=_MADE_AT,
            )
        )
        session.commit()

    listed = _entries(sessions)

    assert [entry["type"] for entry in listed] == ["folder"]


def _stranger_owned_home(session: Session) -> None:
    session.add(
        Folder(
            id=_HOME_ID,
            name="Home",
            user_id=_OTHER_HOME_ID,
            created_at=_MADE_AT,
        )
    )
    session.commit()


def test_a_deck_in_a_folder_i_do_not_own_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _stranger_owned_home(session)
        session.add(
            FlashcardDeck(
                folder_id=_HOME_ID, name="Theirs", created_at=_MADE_AT
            )
        )
        session.commit()

    assert _entries(sessions) == []


def test_a_test_in_a_folder_i_do_not_own_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _stranger_owned_home(session)
        session.add(
            Test(folder_id=_HOME_ID, name="Theirs", created_at=_MADE_AT)
        )
        session.commit()

    assert _entries(sessions) == []


def test_a_file_in_a_folder_i_do_not_own_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        _stranger_owned_home(session)
        session.add(
            File(
                folder_id=_HOME_ID,
                name="theirs",
                extension="pdf",
                created_at=_MADE_AT,
            )
        )
        session.commit()

    assert _entries(sessions) == []
