import random
import uuid

from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import OwnedContent, seeded_content

_SEED = 20260812
_OWNER_COUNT = 4
_GENERATOR = random.Random(_SEED)

OWNERS: tuple[uuid.UUID, ...] = tuple(
    uuid.UUID(int=_GENERATOR.getrandbits(128), version=4)
    for _ in range(_OWNER_COUNT)
)

type World = dict[uuid.UUID, OwnedContent]


def seeded_world(sessions: sessionmaker[Session]) -> World:
    return {owner: seeded_content(sessions, owner) for owner in OWNERS}


def foreign_pairs(world: World) -> list[tuple[uuid.UUID, OwnedContent]]:
    pairs: list[tuple[uuid.UUID, OwnedContent]] = []

    for owner, content in world.items():
        for caller in world:
            if caller != owner:
                pairs.append((caller, content))

    return pairs
