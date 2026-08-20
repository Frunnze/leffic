import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import File, Folder
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_NOT_FOUND = 404
_OK = 200
_UNAUTHORIZED = 401
_UNPROCESSABLE_ENTITY = 422

_HOME_ID = uuid.UUID(USER_ID)
_STRANGER_ID = uuid.UUID(OTHER_USER_ID)
_FILE_ID = "6f1c7d4e-0000-4000-8000-0000000000a1"
_STRANGER_FILE_ID = "6f1c7d4e-0000-4000-8000-0000000000a2"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add_all(
            [
                Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID),
                Folder(id=_STRANGER_ID, name="Home", user_id=_STRANGER_ID),
                File(
                    id=uuid.UUID(_FILE_ID),
                    folder_id=_HOME_ID,
                    name="rome.pdf",
                    extension="pdf",
                ),
                File(
                    id=uuid.UUID(_STRANGER_FILE_ID),
                    folder_id=_STRANGER_ID,
                    name="secret.pdf",
                    extension="pdf",
                ),
            ]
        )
        session.commit()

    return factory


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def _bookmark(client: TestClient, file_id: str, page: int) -> int:
    response = client.put(
        "/file-bookmark",
        json={"file_id": file_id, "page": page},
        headers=authorization(),
    )

    return response.status_code


def test_a_file_starts_without_a_bookmark(client: TestClient) -> None:
    response = client.get(
        "/file-bookmark",
        params={"file_id": _FILE_ID},
        headers=authorization(),
    )

    assert response.status_code == _OK
    assert cast("dict[str, object]", response.json()) == {"page": None}


def test_a_bookmarked_page_is_read_back(client: TestClient) -> None:
    assert _bookmark(client, _FILE_ID, 12) == _OK

    response = client.get(
        "/file-bookmark",
        params={"file_id": _FILE_ID},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json()) == {"page": 12}


def test_bookmarking_again_replaces_the_page(client: TestClient) -> None:
    _ = _bookmark(client, _FILE_ID, 12)
    _ = _bookmark(client, _FILE_ID, 30)

    response = client.get(
        "/file-bookmark",
        params={"file_id": _FILE_ID},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json()) == {"page": 30}


def test_a_bookmark_can_be_removed(client: TestClient) -> None:
    _ = _bookmark(client, _FILE_ID, 12)

    removal = client.delete(
        "/file-bookmark",
        params={"file_id": _FILE_ID},
        headers=authorization(),
    )

    assert removal.status_code == _OK
    assert cast("dict[str, object]", removal.json()) == {"page": None}


def test_another_learner_file_cannot_be_bookmarked(
    client: TestClient,
) -> None:
    assert _bookmark(client, _STRANGER_FILE_ID, 3) == _NOT_FOUND


def test_another_learner_bookmark_cannot_be_read(
    client: TestClient,
) -> None:
    response = client.get(
        "/file-bookmark",
        params={"file_id": _STRANGER_FILE_ID},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND
    assert cast("dict[str, str]", response.json())["detail"] == (
        "File does not exist!"
    )


def test_a_bookmark_needs_a_token(client: TestClient) -> None:
    response = client.get("/file-bookmark", params={"file_id": _FILE_ID})

    assert response.status_code == _UNAUTHORIZED


def test_a_page_before_the_first_is_refused(client: TestClient) -> None:
    assert _bookmark(client, _FILE_ID, 0) == _UNPROCESSABLE_ENTITY
