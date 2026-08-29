import uuid

import pytest
from fastapi import HTTPException
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.study_units.study_unit_access import (
    _MISSING_FLASHCARD,
    MISSING_TEST_ITEM,
    owned_flashcard,
    owned_test_item,
)
from tests.assessment_seeding import seeded_test
from tests.property_support import seeded_deck
from tests.study_unit_access_support import ABSENT_ROW_ID, NOT_FOUND
from tests.support import in_memory_sessions

_SESSIONS = in_memory_sessions()
_EXAMPLES = settings(max_examples=25, deadline=None)


def _refusal(raised: HTTPException) -> tuple[int, object]:
    return raised.status_code, raised.detail


def _seeded_card_id(session: Session, owner: uuid.UUID) -> int:
    _, _, card_ids = seeded_deck(session, owner, 1)

    return card_ids[0]


def _seeded_item_id(session: Session, owner: uuid.UUID) -> int:
    _, _, item_ids = seeded_test(session, owner, 1)

    return item_ids[0]


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_owned_flashcard_property_never_reaches_a_strangers_card(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    with _SESSIONS() as session:
        card_id = _seeded_card_id(session, owner)

        with pytest.raises(HTTPException) as refused:
            _ = owned_flashcard(session, str(stranger), card_id)

    assert _refusal(refused.value) == (NOT_FOUND, _MISSING_FLASHCARD)


@_EXAMPLES
@given(st.uuids())
def test_owned_flashcard_property_returns_the_card_it_was_asked_for(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        card_id = _seeded_card_id(session, owner)
        card = owned_flashcard(session, str(owner), card_id)

        assert card.id == card_id


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_owned_flashcard_property_refuses_absent_and_foreign_ids_alike(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    with _SESSIONS() as session:
        card_id = _seeded_card_id(session, owner)

        with pytest.raises(HTTPException) as foreign:
            _ = owned_flashcard(session, str(stranger), card_id)

        with pytest.raises(HTTPException) as absent:
            _ = owned_flashcard(session, str(stranger), ABSENT_ROW_ID)

    assert _refusal(foreign.value) == _refusal(absent.value)


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_owned_test_item_property_never_reaches_a_strangers_item(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    with _SESSIONS() as session:
        item_id = _seeded_item_id(session, owner)

        with pytest.raises(HTTPException) as refused:
            _ = owned_test_item(session, str(stranger), item_id)

    assert _refusal(refused.value) == (NOT_FOUND, MISSING_TEST_ITEM)


@_EXAMPLES
@given(st.uuids())
def test_owned_test_item_property_returns_the_item_it_was_asked_for(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        item_id = _seeded_item_id(session, owner)
        item = owned_test_item(session, str(owner), item_id)

        assert item.id == item_id


@_EXAMPLES
@given(st.uuids(), st.uuids())
def test_owned_test_item_property_refuses_absent_and_foreign_ids_alike(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    _ = assume(owner != stranger)

    with _SESSIONS() as session:
        item_id = _seeded_item_id(session, owner)

        with pytest.raises(HTTPException) as foreign:
            _ = owned_test_item(session, str(stranger), item_id)

        with pytest.raises(HTTPException) as absent:
            _ = owned_test_item(session, str(stranger), ABSENT_ROW_ID)

    assert _refusal(foreign.value) == _refusal(absent.value)


@_EXAMPLES
@given(st.uuids(), st.integers(min_value=10**6, max_value=ABSENT_ROW_ID))
def test_owned_flashcard_property_refuses_every_id_no_deck_carries(
    owner: uuid.UUID, unseeded_id: int
) -> None:
    with _SESSIONS() as session:
        _ = _seeded_card_id(session, owner)

        with pytest.raises(HTTPException) as refused:
            _ = owned_flashcard(session, str(owner), unseeded_id)

    assert _refusal(refused.value) == (NOT_FOUND, _MISSING_FLASHCARD)


@_EXAMPLES
@given(st.uuids(), st.integers(min_value=10**6, max_value=ABSENT_ROW_ID))
def test_owned_test_item_property_refuses_every_id_no_test_carries(
    owner: uuid.UUID, unseeded_id: int
) -> None:
    with _SESSIONS() as session:
        _ = _seeded_item_id(session, owner)

        with pytest.raises(HTTPException) as refused:
            _ = owned_test_item(session, str(owner), unseeded_id)

    assert _refusal(refused.value) == (NOT_FOUND, MISSING_TEST_ITEM)
