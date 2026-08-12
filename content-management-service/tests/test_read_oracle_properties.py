import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    MISSING_NOTE,
    crashless_client,
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


def test_a_foreign_note_reads_like_an_unknown_note(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        headers = authorization(str(caller))
        foreign = read_unit(
            client, "/note", "note_id", victim.note_id, headers
        )
        unknown = read_unit(
            client, "/note", "note_id", str(uuid.uuid4()), headers
        )

        assert foreign == unknown


def test_a_foreign_deck_reads_like_an_unknown_deck(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        headers = authorization(str(caller))
        foreign = read_unit(
            client,
            "/flashcards",
            "flashcard_deck_id",
            victim.deck_id,
            headers,
        )
        unknown = read_unit(
            client,
            "/flashcards",
            "flashcard_deck_id",
            str(uuid.uuid4()),
            headers,
        )

        assert foreign == unknown


def test_a_foreign_test_reads_like_an_unknown_test(
    client: TestClient, world: World
) -> None:
    for caller, victim in foreign_pairs(world):
        headers = authorization(str(caller))
        foreign = read_unit(
            client, "/test-items", "test_id", victim.test_id, headers
        )
        unknown = read_unit(
            client, "/test-items", "test_id", str(uuid.uuid4()), headers
        )

        assert foreign == unknown


def test_every_intruder_meets_the_same_refusal(
    client: TestClient, world: World
) -> None:
    for owner, content in world.items():
        refusals = [
            read_unit(
                client,
                "/note",
                "note_id",
                content.note_id,
                authorization(str(caller)),
            )
            for caller in world
            if caller != owner
        ]

        assert refusals.count(refusals[0]) == len(refusals)
        assert refusals[0][0] == 404
        assert refusals[0][1]["detail"] == MISSING_NOTE
