import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import File, FlashcardDeck, Folder, Note, Test
from tests.access_support import HOME_ID, OTHER_HOME_ID, scoped_client
from tests.support import authorization, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def foreign_folder_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.add(
            Folder(id=OTHER_HOME_ID, name="Home", user_id=OTHER_HOME_ID)
        )
        session.commit()
        folder = Folder(
            parent_id=OTHER_HOME_ID,
            name="Private Research",
            user_id=OTHER_HOME_ID,
        )
        session.add(folder)
        session.commit()
        session.add_all(
            [
                Note(
                    folder_id=folder.id,
                    name="Confidential",
                    content="secret",
                    type="general",
                ),
                FlashcardDeck(folder_id=folder.id, name="Their deck"),
                Test(folder_id=folder.id, name="Their quiz"),
                File(folder_id=folder.id, name="theirs", extension="pdf"),
                Folder(
                    parent_id=folder.id,
                    name="Their subfolder",
                    user_id=OTHER_HOME_ID,
                ),
            ]
        )
        session.commit()

        return str(folder.id)


def _access(client: TestClient, folder_id: str) -> dict[str, object]:
    response = client.get(
        "/access-folder/",
        params={"folder_id": folder_id},
        headers=authorization(),
    )

    return cast("dict[str, object]", response.json())


def test_another_users_folder_name_is_not_revealed(
    client: TestClient, foreign_folder_id: str
) -> None:
    body = _access(client, foreign_folder_id)

    assert body["parent_folder_name"] == "Home"


def test_another_users_notes_are_not_listed(
    client: TestClient, foreign_folder_id: str
) -> None:
    body = _access(client, foreign_folder_id)
    listed = cast("list[dict[str, str]]", body["content"])

    assert listed == []


def test_a_foreign_folder_reads_like_an_unknown_one(
    client: TestClient, foreign_folder_id: str
) -> None:
    foreign = _access(client, foreign_folder_id)
    unknown = _access(client, str(uuid.uuid4()))

    assert foreign == unknown



def test_your_own_notes_are_still_listed(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()
        session.add(
            Note(
                folder_id=HOME_ID,
                name="Mine",
                content="body",
                type="general",
            )
        )
        session.commit()

    body = _access(client, str(HOME_ID))
    listed = cast("list[dict[str, str]]", body["content"])

    assert [entry["name"] for entry in listed] == ["Mine"]


def test_the_owner_still_sees_their_folder_name(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()
        mine = Folder(parent_id=HOME_ID, name="Biology", user_id=HOME_ID)
        session.add(mine)
        session.commit()
        mine_id = str(mine.id)

    assert _access(client, mine_id)["parent_folder_name"] == "Biology"


def test_another_users_notes_survive_being_listed(
    client: TestClient,
    sessions: sessionmaker[Session],
    foreign_folder_id: str,
) -> None:
    _ = _access(client, foreign_folder_id)

    with sessions() as session:
        assert session.query(Note).count() == 1


def test_a_foreign_subfolder_is_not_listed(
    client: TestClient, foreign_folder_id: str
) -> None:
    body = _access(client, foreign_folder_id)
    listed = cast("list[dict[str, str]]", body["content"])
    kinds = {entry["type"] for entry in listed}

    assert "folder" not in kinds


