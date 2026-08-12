import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from shared.content_access import owned_content
from shared.models import File, FlashcardDeck, Note, Test
from tests.access_support import (
    HOME_ID,
    MISSING_UNIT,
    OTHER_HOME_ID,
    seeded_content,
)
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions

_CUSTOM_DETAIL = "Deck does not exist!"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


def test_an_owned_deck_is_returned_to_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        unit = owned_content(
            session, USER_ID, FlashcardDeck, owned.deck_id, MISSING_UNIT
        )

    assert str(unit.id) == owned.deck_id


def test_an_owned_test_is_returned_to_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        unit = owned_content(
            session, USER_ID, Test, owned.test_id, MISSING_UNIT
        )

    assert str(unit.id) == owned.test_id


def test_an_owned_note_is_returned_to_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        unit = owned_content(
            session, USER_ID, Note, owned.note_id, MISSING_UNIT
        )

    assert str(unit.id) == owned.note_id


def test_an_owned_file_is_returned_to_its_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        unit = owned_content(
            session, USER_ID, File, owned.file_id, MISSING_UNIT
        )

    assert str(unit.id) == owned.file_id


def test_a_deck_owned_by_another_user_is_hidden(
    sessions: sessionmaker[Session],
) -> None:
    theirs = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_content(
            session, USER_ID, FlashcardDeck, theirs.deck_id, MISSING_UNIT
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_UNIT


def test_a_unit_that_was_never_created_is_reported_as_missing(
    sessions: sessionmaker[Session],
) -> None:
    _ = seeded_content(sessions, HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_content(
            session, USER_ID, FlashcardDeck, str(uuid.uuid4()), MISSING_UNIT
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_UNIT


def test_a_malformed_unit_id_is_reported_as_missing(
    sessions: sessionmaker[Session],
) -> None:
    _ = seeded_content(sessions, HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_content(
            session, USER_ID, FlashcardDeck, "not-a-uuid", MISSING_UNIT
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == MISSING_UNIT


def test_the_detail_the_caller_passes_is_the_detail_reported(
    sessions: sessionmaker[Session],
) -> None:
    theirs = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_content(
            session, USER_ID, FlashcardDeck, theirs.deck_id, _CUSTOM_DETAIL
        )

    assert raised.value.detail == _CUSTOM_DETAIL


def test_a_note_id_never_resolves_to_a_deck(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_content(
            session, USER_ID, FlashcardDeck, owned.note_id, MISSING_UNIT
        )

    assert raised.value.status_code == 404


def test_an_owned_deck_is_found_among_other_owners_decks(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)
    _ = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session:
        unit = owned_content(
            session, USER_ID, FlashcardDeck, owned.deck_id, MISSING_UNIT
        )

    assert str(unit.id) == owned.deck_id


def test_a_neighbours_deck_stays_hidden_from_the_other_owner(
    sessions: sessionmaker[Session],
) -> None:
    owned = seeded_content(sessions, HOME_ID)
    _ = seeded_content(sessions, OTHER_HOME_ID)

    with sessions() as session, pytest.raises(HTTPException) as raised:
        _ = owned_content(
            session,
            OTHER_USER_ID,
            FlashcardDeck,
            owned.deck_id,
            MISSING_UNIT,
        )

    assert raised.value.status_code == 404
