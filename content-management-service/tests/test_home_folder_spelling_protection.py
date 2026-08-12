from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    HOME_ID,
    MISSING_FOLDER,
    OTHER_HOME_ID,
    PROTECTED_HOME,
    OwnedContent,
    identifier_spellings,
    scoped_client,
    seeded_content,
    surviving_folder_ids,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def intruder(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


def _delete_folder(
    client: TestClient, spelling: str, headers: dict[str, str]
) -> tuple[int, dict[str, str]]:
    response = client.request(
        "DELETE",
        "/delete-folder/",
        params={"folder_id": spelling},
        headers=headers,
    )

    return response.status_code, response.json()


def test_no_spelling_of_your_home_folder_can_delete_it(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    for spelling in identifier_spellings(owned.home_id):
        code, body = _delete_folder(client, spelling, authorization())

        assert code == 422
        assert body == {"detail": PROTECTED_HOME}

    assert owned.home_id in surviving_folder_ids(sessions)


def test_no_spelling_of_a_foreign_home_folder_reports_protection(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    for spelling in identifier_spellings(owned.home_id):
        code, body = _delete_folder(client, spelling, intruder)

        assert code == 404
        assert body == {"detail": MISSING_FOLDER}

    assert owned.home_id in surviving_folder_ids(sessions)
