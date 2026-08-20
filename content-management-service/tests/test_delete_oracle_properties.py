import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import crashless_client, delete_unit
from tests.scope_world import World, foreign_pairs, seeded_world
from tests.support import authorization, in_memory_sessions


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def world(sessions: sessionmaker[Session]) -> World:
    return seeded_world(sessions)


def test_deleting_an_unknown_id_reads_like_deleting_a_foreign_one(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        headers = authorization(str(caller))
        foreign = delete_unit(
            client, "/delete-deck/", "deck_id", victim.deck_id, headers
        )
        unknown = delete_unit(
            client, "/delete-deck/", "deck_id", str(uuid.uuid4()), headers
        )

        assert foreign == unknown


def test_a_foreign_file_reads_like_an_unknown_file(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        headers = authorization(str(caller))
        foreign = delete_unit(
            client, "/delete-file/", "file_id", victim.file_id, headers
        )
        unknown = delete_unit(
            client, "/delete-file/", "file_id", str(uuid.uuid4()), headers
        )

        assert foreign == unknown


def test_a_foreign_folder_reads_like_an_unknown_folder(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        headers = authorization(str(caller))
        foreign = delete_unit(
            client, "/delete-folder/", "folder_id", victim.folder_id, headers
        )
        unknown = delete_unit(
            client,
            "/delete-folder/",
            "folder_id",
            str(uuid.uuid4()),
            headers,
        )

        assert foreign == unknown
