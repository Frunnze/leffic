from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import Folder
from tests.access_support import HOME_ID, MISSING_FOLDER, crashless_client
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.support import authorization, in_memory_sessions

_INTERNAL_SERVER_ERROR = 500
_NOT_FOUND = 404

_MALFORMED = ("not-a-uuid", "' OR 1=1 --", "12345", "üñíçø∂é")


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()

    yield from crashless_client(sessions)


@pytest.mark.parametrize("folder_id", _MALFORMED)
def test_creating_a_folder_under_a_malformed_parent_is_not_found(
    client: TestClient, folder_id: str
) -> None:
    response = client.post(
        "/create-folder",
        json={"parent_folder_id": folder_id, "folder_name": "Mine"},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND
    assert response.json()["detail"] == MISSING_FOLDER


@pytest.mark.parametrize("folder_id", _MALFORMED)
def test_moving_a_unit_to_a_malformed_folder_is_not_found(
    client: TestClient, folder_id: str
) -> None:
    response = client.patch(
        "/move-unit",
        json={
            "unit_id": str(HOME_ID),
            "unit_type": "folder",
            "folder_id": folder_id,
        },
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


@pytest.mark.parametrize("folder_id", _MALFORMED)
def test_note_stats_for_a_malformed_folder_are_not_found(
    client: TestClient, folder_id: str
) -> None:
    response = client.get(
        "/notes-stats",
        params={"folder_id": folder_id},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND
    assert response.json()["detail"] == MISSING_FOLDER


@pytest.mark.parametrize("folder_id", _MALFORMED)
def test_flashcard_stats_for_a_malformed_folder_are_not_found(
    client: TestClient, folder_id: str
) -> None:
    response = client.get(
        "/flashcards-stats",
        params={"folder_id": folder_id},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


@pytest.mark.parametrize("folder_id", _MALFORMED)
def test_flashcards_for_a_malformed_folder_are_not_found(
    client: TestClient, folder_id: str
) -> None:
    response = client.get(
        "/flashcards",
        params={"folder_id": folder_id},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


@pytest.mark.parametrize("folder_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_folder_id_never_crashes(
    client: TestClient, folder_id: str
) -> None:
    response = client.get(
        "/notes-stats",
        params={"folder_id": folder_id},
        headers=authorization(),
    )

    assert response.status_code != _INTERNAL_SERVER_ERROR
