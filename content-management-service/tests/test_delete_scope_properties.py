from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import File, FlashcardDeck, Note, Test
from tests.access_support import (
    MISSING_FILE,
    MISSING_FOLDER,
    MISSING_UNIT,
    crashless_client,
    delete_unit,
    surviving_folder_ids,
    surviving_ids,
)
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


def test_no_user_can_delete_another_users_deck(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = delete_unit(
            client,
            "/delete-deck/",
            "deck_id",
            victim.deck_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_UNIT

    assert surviving_ids(sessions, FlashcardDeck) == {
        content.deck_id for content in world.values()
    }


def test_no_user_can_delete_another_users_test(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = delete_unit(
            client,
            "/delete-test/",
            "test_id",
            victim.test_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_UNIT

    assert surviving_ids(sessions, Test) == {
        content.test_id for content in world.values()
    }


def test_no_user_can_delete_another_users_note(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = delete_unit(
            client,
            "/delete-note/",
            "note_id",
            victim.note_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_UNIT

    assert surviving_ids(sessions, Note) == {
        content.note_id for content in world.values()
    }


def test_no_user_can_delete_another_users_file(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = delete_unit(
            client,
            "/delete-file/",
            "file_id",
            victim.file_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_FILE

    assert surviving_ids(sessions, File) == {
        content.file_id for content in world.values()
    }


def test_no_user_can_delete_another_users_folder(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = delete_unit(
            client,
            "/delete-folder/",
            "folder_id",
            victim.folder_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_FOLDER

    assert {content.folder_id for content in world.values()} <= (
        surviving_folder_ids(sessions)
    )
