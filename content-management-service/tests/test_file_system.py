import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from src.app_factory import create_app
from src.shared.database import get_db
from src.shared.models import (
    File,
    FlashcardDeck,
    Folder,
    Note,
    Test,
)
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def _home_folder(session: Session) -> Folder:
    folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
    session.add(folder)
    session.commit()

    return folder


def test_creating_a_folder_returns_its_identity(client: TestClient) -> None:
    response = client.post(
        "/create-folder",
        json={"parent_folder_id": "home", "folder_name": "Biology"},
        headers=authorization(),
    )

    body = cast("dict[str, str]", response.json())

    assert body["folder_name"] == "Biology"
    assert body["parent_folder_id"] == USER_ID


def test_a_second_folder_with_the_same_name_is_numbered(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(
            Folder(parent_id=_HOME_ID, name="Biology", user_id=_HOME_ID)
        )
        session.commit()

    response = client.post(
        "/create-folder",
        json={"parent_folder_id": "home", "folder_name": "Biology"},
        headers=authorization(),
    )

    assert cast("dict[str, str]", response.json())["folder_name"] == (
        "Biology 2"
    )


def test_creating_a_folder_needs_a_parent(client: TestClient) -> None:
    response = client.post(
        "/create-folder",
        json={"folder_name": "Orphan"},
        headers=authorization(),
    )

    assert response.status_code == 422


def test_accessing_home_creates_it_when_missing(client: TestClient) -> None:
    response = client.get(
        "/access-folder/",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    body = cast("dict[str, object]", response.json())

    assert body == {"content": [], "parent_folder_name": "Home"}


def test_accessing_home_lists_its_contents(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        session.add(
            Note(
                folder_id=folder.id,
                name="N",
                content="c",
                type="general",
            )
        )
        session.commit()

    response = client.get(
        "/access-folder/",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    body = cast("dict[str, list[dict[str, str]]]", response.json())

    assert body["content"][0]["type"] == "note"


def test_accessing_a_folder_lists_every_kind_of_child(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        session.add(Folder(parent_id=folder.id, name="Sub", user_id=_HOME_ID))
        session.add(FlashcardDeck(folder_id=folder.id, name="Deck"))
        session.add(Test(folder_id=folder.id, name="Quiz"))
        session.add(
            File(folder_id=folder.id, name="doc", extension="pdf")
        )
        session.commit()

    response = client.get(
        "/access-folder/",
        params={"folder_id": str(_HOME_ID)},
        headers=authorization(),
    )

    body = cast("dict[str, list[dict[str, str]]]", response.json())
    kinds = {entry["type"] for entry in body["content"]}

    assert kinds == {"folder", "flashcard_deck", "test", "file"}


def test_accessing_an_unknown_folder_falls_back_to_home(
    client: TestClient,
) -> None:
    response = client.get(
        "/access-folder/",
        params={"folder_id": str(uuid.uuid4())},
        headers=authorization(),
    )

    body = cast("dict[str, object]", response.json())

    assert body["parent_folder_name"] == "Home"


def test_accessing_needs_a_folder_id(client: TestClient) -> None:
    response = client.get("/access-folder/", headers=authorization())

    assert response.status_code == 422
