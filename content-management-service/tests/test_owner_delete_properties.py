from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import FlashcardDeck, Note
from tests.access_support import (
    MISSING_FOLDER,
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


def test_no_user_can_delete_another_users_home_folder(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = delete_unit(
            client,
            "/delete-folder/",
            "folder_id",
            victim.home_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_FOLDER

    assert {content.home_id for content in world.values()} <= (
        surviving_folder_ids(sessions)
    )


def test_every_owner_still_deletes_their_own_deck(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for owner, content in world.items():
        code, body = delete_unit(
            client,
            "/delete-deck/",
            "deck_id",
            content.deck_id,
            authorization(str(owner)),
        )

        assert code == 200
        assert body == {"msg": "Deck deleted!"}

    assert surviving_ids(sessions, FlashcardDeck) == set()


def test_every_owner_still_deletes_their_own_subfolder(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for owner, content in world.items():
        code, body = delete_unit(
            client,
            "/delete-folder/",
            "folder_id",
            content.folder_id,
            authorization(str(owner)),
        )

        assert code == 200
        assert body == {"msg": "Folder deleted!"}

    assert surviving_folder_ids(sessions) == {
        content.home_id for content in world.values()
    }


def test_a_refused_delete_leaves_the_owner_free_to_delete(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        _ = delete_unit(
            client,
            "/delete-note/",
            "note_id",
            victim.note_id,
            authorization(str(caller)),
        )

    for owner, content in world.items():
        code, _body = delete_unit(
            client,
            "/delete-note/",
            "note_id",
            content.note_id,
            authorization(str(owner)),
        )

        assert code == 200

    assert surviving_ids(sessions, Note) == set()
