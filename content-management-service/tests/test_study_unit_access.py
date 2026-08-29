import inspect

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import study_unit_access
from features.study_units.study_unit_access import (
    _MISSING_FLASHCARD,
    MISSING_TEST_ITEM,
    owned_flashcard,
    owned_test_item,
)
from shared import content_access
from shared.models import Flashcard
from tests.study_unit_access_support import (
    ABSENT_ROW_ID,
    NOT_FOUND,
    StudyUnitWorld,
)

_OWNED_CONTENT_PARAMETERS = (
    "db",
    "user_id",
    "model",
    "unit_id",
    "missing_detail",
)
_PUBLIC_HELPERS = {"owned_flashcard", "owned_test_item"}
_HOSTILE_ROW_IDS = (0, -1, ABSENT_ROW_ID)


def _defined_functions(module: object) -> set[str]:
    return {
        name
        for name, member in inspect.getmembers(module, inspect.isfunction)
        if member.__module__ == getattr(module, "__name__", "")
    }


def test_missing_flashcard_detail_is_the_module_constant() -> None:
    assert _MISSING_FLASHCARD == "Flashcard does not exist!"


def test_missing_test_item_detail_is_the_module_constant() -> None:
    assert MISSING_TEST_ITEM == "Test item does not exist!"


def test_owned_flashcard_returns_the_owners_card(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session:
        card = owned_flashcard(
            session, str(world.owner), world.flashcard_id
        )

        assert card.id == world.flashcard_id


def test_owned_flashcard_refuses_a_strangers_card_with_the_missing_detail(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session, pytest.raises(HTTPException) as refused:
        _ = owned_flashcard(
            session, str(world.stranger), world.flashcard_id
        )

    assert refused.value.status_code == NOT_FOUND
    assert refused.value.detail == _MISSING_FLASHCARD


def test_owned_flashcard_absent_id_is_the_same_404(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session:
        with pytest.raises(HTTPException) as absent:
            _ = owned_flashcard(session, str(world.owner), ABSENT_ROW_ID)

        with pytest.raises(HTTPException) as stranger:
            _ = owned_flashcard(
                session, str(world.stranger), world.flashcard_id
            )

    assert (absent.value.status_code, absent.value.detail) == (
        stranger.value.status_code,
        stranger.value.detail,
    )


def test_owned_test_item_returns_the_owners_item(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session:
        item = owned_test_item(
            session, str(world.owner), world.test_item_id
        )

        assert item.id == world.test_item_id


def test_owned_test_item_refuses_a_strangers_item_with_the_detail(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session, pytest.raises(HTTPException) as refused:
        _ = owned_test_item(
            session, str(world.stranger), world.test_item_id
        )

    assert refused.value.status_code == NOT_FOUND
    assert refused.value.detail == MISSING_TEST_ITEM


def test_owned_test_item_absent_id_is_the_same_404(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session:
        with pytest.raises(HTTPException) as absent:
            _ = owned_test_item(session, str(world.owner), ABSENT_ROW_ID)

        with pytest.raises(HTTPException) as stranger:
            _ = owned_test_item(
                session, str(world.stranger), world.test_item_id
            )

    assert (absent.value.status_code, absent.value.detail) == (
        stranger.value.status_code,
        stranger.value.detail,
    )


def test_module_exposes_only_the_two_named_helpers() -> None:
    assert _defined_functions(study_unit_access) == _PUBLIC_HELPERS


def test_content_access_is_untouched() -> None:
    parameters = inspect.signature(content_access.owned_content).parameters

    assert tuple(parameters) == _OWNED_CONTENT_PARAMETERS
    assert _defined_functions(content_access) == {"owned_content"}


def test_the_two_helpers_refuse_with_different_details() -> None:
    assert _MISSING_FLASHCARD != MISSING_TEST_ITEM


def test_a_flashcard_helper_never_answers_with_a_test_item(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session:
        card = owned_flashcard(
            session, str(world.owner), world.flashcard_id
        )

        assert isinstance(card, Flashcard)


@pytest.mark.parametrize("hostile_id", _HOSTILE_ROW_IDS)
def test_a_hostile_flashcard_id_is_refused_as_a_missing_card(
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
    hostile_id: int,
) -> None:
    with sessions() as session, pytest.raises(HTTPException) as refused:
        _ = owned_flashcard(session, str(world.owner), hostile_id)

    assert refused.value.status_code == NOT_FOUND


@pytest.mark.parametrize("hostile_id", _HOSTILE_ROW_IDS)
def test_a_hostile_test_item_id_is_refused_as_a_missing_item(
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
    hostile_id: int,
) -> None:
    with sessions() as session, pytest.raises(HTTPException) as refused:
        _ = owned_test_item(session, str(world.owner), hostile_id)

    assert refused.value.status_code == NOT_FOUND
