from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    MISSING_DECK,
    MISSING_NOTE,
    MISSING_TEST,
    crashless_client,
    opened_test_sessions,
    read_unit,
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


def test_no_user_can_read_another_users_note(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = read_unit(
            client,
            "/note",
            "note_id",
            victim.note_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_NOTE


def test_no_user_can_read_another_users_deck_cards(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = read_unit(
            client,
            "/flashcards",
            "flashcard_deck_id",
            victim.deck_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_DECK


def test_no_user_can_read_another_users_test_items(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        code, body = read_unit(
            client,
            "/test-items",
            "test_id",
            victim.test_id,
            authorization(str(caller)),
        )

        assert code == 404
        assert body["detail"] == MISSING_TEST


def test_refused_readings_open_no_test_session(
    client: TestClient, sessions: sessionmaker[Session], world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        _ = read_unit(
            client,
            "/test-items",
            "test_id",
            victim.test_id,
            authorization(str(caller)),
        )

    assert opened_test_sessions(sessions) == 0


def test_every_owner_still_reads_their_own_note(
    client: TestClient, world: World
) -> None:
    for owner, content in world.items():
        code, body = read_unit(
            client,
            "/note",
            "note_id",
            content.note_id,
            authorization(str(owner)),
        )

        assert code == 200
        assert body == {"content": "body", "name": "N", "read": False}


def test_every_owner_still_reads_their_own_deck_cards(
    client: TestClient, world: World
) -> None:
    for owner, content in world.items():
        code, body = read_unit(
            client,
            "/flashcards",
            "flashcard_deck_id",
            content.deck_id,
            authorization(str(owner)),
        )

        assert code == 200
        assert body["total_flashcards"] == 1


def test_every_owner_still_reads_their_own_test_items(
    client: TestClient, world: World
) -> None:
    for owner, content in world.items():
        code, body = read_unit(
            client,
            "/test-items",
            "test_id",
            content.test_id,
            authorization(str(owner)),
        )

        assert code == 200
        assert body["total_items"] == 1
