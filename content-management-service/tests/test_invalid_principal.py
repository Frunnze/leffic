import uuid
from collections.abc import Iterator

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import crashless_client
from tests.support import in_memory_sessions

_INTERNAL_SERVER_ERROR = 500
_UNAUTHORIZED = 401

_SCOPED_REQUESTS: tuple[tuple[str, str, str], ...] = (
    ("GET", "/note", "note_id"),
    ("DELETE", "/delete-deck/", "deck_id"),
    ("DELETE", "/delete-test/", "test_id"),
    ("DELETE", "/delete-note/", "note_id"),
    ("DELETE", "/delete-file/", "file_id"),
    ("DELETE", "/delete-folder/", "folder_id"),
    ("GET", "/flashcards", "flashcard_deck_id"),
    ("GET", "/test-items", "test_id"),
)

_NON_UUID_CLAIMS: tuple[str, ...] = (
    "hello",
    "",
    "home",
    "6f1c7d4e-0000-4000-8000",
    "' OR 1=1 --",
)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


def _headers(user_id: str) -> dict[str, str]:
    token = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(("method", "path", "parameter"), _SCOPED_REQUESTS)
@pytest.mark.parametrize("claim", _NON_UUID_CLAIMS)
def test_a_principal_that_is_not_a_uuid_is_rejected(
    client: TestClient,
    method: str,
    path: str,
    parameter: str,
    claim: str,
) -> None:
    response = client.request(
        method,
        path,
        params={parameter: str(uuid.uuid4())},
        headers=_headers(claim),
    )

    assert response.status_code == _UNAUTHORIZED


@pytest.mark.parametrize(("method", "path", "parameter"), _SCOPED_REQUESTS)
def test_a_principal_that_is_not_a_uuid_never_crashes(
    client: TestClient, method: str, path: str, parameter: str
) -> None:
    response = client.request(
        method,
        path,
        params={parameter: str(uuid.uuid4())},
        headers=_headers("hello"),
    )

    assert response.status_code != _INTERNAL_SERVER_ERROR
