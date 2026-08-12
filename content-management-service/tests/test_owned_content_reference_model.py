import itertools
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from shared.content_access import ContentModel, owned_content
from shared.models import File, FlashcardDeck, Folder, Note, Test
from tests.access_support import MISSING_UNIT
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.scope_world import World, seeded_world
from tests.support import in_memory_sessions

_MODELS: tuple[ContentModel, ...] = (FlashcardDeck, Test, Note, File)
_HOSTILE_SAMPLE = 10
_UNKNOWN_IDS: tuple[str, ...] = tuple(
    str(uuid.UUID(int=index)) for index in range(1, 4)
)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def world(sessions: sessionmaker[Session]) -> World:
    return seeded_world(sessions)


def _scanned_answer(
    session: Session,
    caller: uuid.UUID,
    model: ContentModel,
    raw_id: str,
) -> str | None:
    try:
        wanted = uuid.UUID(raw_id)
    except ValueError:
        return None

    for row in session.query(model).all():
        folder = session.get(Folder, row.folder_id)

        if row.id == wanted and folder is not None:
            return str(row.id) if folder.user_id == caller else None

    return None


def _looked_up_answer(
    session: Session,
    caller: uuid.UUID,
    model: ContentModel,
    raw_id: str,
) -> str | None:
    try:
        unit = owned_content(
            session, str(caller), model, raw_id, MISSING_UNIT
        )
    except HTTPException:
        return None

    return str(unit.id)


def _candidate_ids(world: World) -> list[str]:
    candidates: list[str] = []

    for content in world.values():
        candidates.extend(
            (
                content.deck_id,
                content.test_id,
                content.note_id,
                content.file_id,
                content.folder_id,
                content.home_id,
            )
        )

    candidates.extend(_UNKNOWN_IDS)
    candidates.extend(HOSTILE_IDENTIFIERS[:_HOSTILE_SAMPLE])

    return candidates


def test_the_ownership_lookup_matches_a_plain_row_scan(
    sessions: sessionmaker[Session], world: World
) -> None:
    candidates = _candidate_ids(world)

    with sessions() as session:
        for caller, model, raw_id in itertools.product(
            world, _MODELS, candidates
        ):
            assert _looked_up_answer(
                session, caller, model, raw_id
            ) == _scanned_answer(session, caller, model, raw_id)


def test_the_ownership_lookup_finds_every_owners_own_unit(
    sessions: sessionmaker[Session], world: World
) -> None:
    with sessions() as session:
        for owner, content in world.items():
            found = [
                _looked_up_answer(session, owner, model, unit_id)
                for model, unit_id in zip(
                    _MODELS,
                    (
                        content.deck_id,
                        content.test_id,
                        content.note_id,
                        content.file_id,
                    ),
                    strict=True,
                )
            ]

            assert found == [
                content.deck_id,
                content.test_id,
                content.note_id,
                content.file_id,
            ]
