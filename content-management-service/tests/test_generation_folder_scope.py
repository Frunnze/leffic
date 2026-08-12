from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import Folder, Note
from tests.access_support import (
    HOME_ID,
    MISSING_FOLDER,
    MISSING_NOTE,
    OTHER_HOME_ID,
    crashless_client,
)
from tests.support import authorization, in_memory_sessions

_MALFORMED = ("not-a-uuid", "' OR 1=1 --")


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def foreign_folder_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.add(
            Folder(id=OTHER_HOME_ID, name="Home", user_id=OTHER_HOME_ID)
        )
        session.commit()
        folder = Folder(
            parent_id=OTHER_HOME_ID, name="Theirs", user_id=OTHER_HOME_ID
        )
        session.add(folder)
        session.commit()

        return str(folder.id)


def _generate(client: TestClient, folder_id: str) -> int:
    response = client.post(
        "/generate-study-units",
        json={
            "text": "Mitochondria are the powerhouse of the cell.",
            "folder_id": folder_id,
            "note": {"verbosity": "brief"},
        },
        headers=authorization(),
    )

    return response.status_code


def test_units_cannot_be_generated_into_another_users_folder(
    client: TestClient, foreign_folder_id: str
) -> None:
    assert _generate(client, foreign_folder_id) == 404


def test_generating_into_a_foreign_folder_writes_nothing(
    client: TestClient,
    sessions: sessionmaker[Session],
    foreign_folder_id: str,
) -> None:
    _ = _generate(client, foreign_folder_id)

    with sessions() as session:
        assert session.query(Note).count() == 0


def test_units_cannot_be_generated_into_a_missing_folder(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()

    assert _generate(client, str(OTHER_HOME_ID)) == 404


@pytest.mark.parametrize("folder_id", _MALFORMED)
def test_units_cannot_be_generated_into_a_malformed_folder(
    client: TestClient, sessions: sessionmaker[Session], folder_id: str
) -> None:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()

    assert _generate(client, folder_id) == 404


@pytest.mark.parametrize("note_id", _MALFORMED)
def test_reviewing_a_malformed_note_is_not_found(
    client: TestClient, note_id: str
) -> None:
    response = client.post(
        "/review-note",
        json={"note_id": note_id},
        headers=authorization(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == MISSING_NOTE


def test_reviewing_another_users_note_is_not_found(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(
            Folder(id=OTHER_HOME_ID, name="Home", user_id=OTHER_HOME_ID)
        )
        session.commit()
        note = Note(
            folder_id=OTHER_HOME_ID,
            name="Theirs",
            content="secret",
            type="general",
        )
        session.add(note)
        session.commit()
        note_id = str(note.id)

    response = client.post(
        "/review-note",
        json={"note_id": note_id},
        headers=authorization(),
    )

    with sessions() as session:
        still_unread = session.query(Note).one().read

    assert response.status_code == 404
    assert still_unread is False


def test_a_missing_parent_folder_is_reported_for_generation(
    client: TestClient,
) -> None:
    assert _generate(client, str(OTHER_HOME_ID)) == 404
    assert MISSING_FOLDER
