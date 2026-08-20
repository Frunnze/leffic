import uuid

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.flashcard_deck_writer import (
    MissingDeckError,
    _existing_deck,
    append_flashcards,
    create_flashcard_deck,
    name_deck_once,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import PENDING_NAME
from shared.models import Flashcard, FlashcardDeck
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)
_CARD = st.fixed_dictionaries({"front": st.text(max_size=6)})
_TYPES = st.sampled_from(["basic", "cloze", "feynman", "list"])
_NAMES = st.text(min_size=1, max_size=10).filter(
    lambda name: name != PENDING_NAME
)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test__existing_deck_property_refuses_a_deck_that_is_not_there(
    owner: uuid.UUID, absent: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )

        assert str(_existing_deck(session, deck_id).id) == deck_id

        with pytest.raises(MissingDeckError) as refused:
            _ = _existing_deck(session, str(absent))

        assert str(refused.value) == "Flashcard deck does not exist!"


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_create_flashcard_deck_property_starts_out_awaiting_its_name(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )
        deck = session.get(FlashcardDeck, uuid.UUID(deck_id))

        assert deck is not None
        assert deck.name == PENDING_NAME
        assert str(deck.folder_id) == str(folder_id)
        assert deck.flashcards == []


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _TYPES, st.lists(_CARD, max_size=4))
def test_append_flashcards_property_writes_every_card_under_its_type(
    owner: uuid.UUID, flashcard_type: str, cards: list[dict[str, str]]
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )
        written = append_flashcards(
            session, deck_id, flashcard_type, cards
        )
        saved = (
            session.query(Flashcard)
            .filter(Flashcard.deck_id == uuid.UUID(deck_id))
            .all()
        )

        assert written == len(cards)
        assert len(saved) == len(cards)
        assert all(card.type == flashcard_type for card in saved)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _TYPES, st.lists(_CARD, max_size=3))
def test_append_flashcards_property_adds_to_what_is_already_there(
    owner: uuid.UUID, flashcard_type: str, cards: list[dict[str, str]]
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )
        first = append_flashcards(session, deck_id, "basic", cards)
        second = append_flashcards(
            session, deck_id, flashcard_type, cards
        )
        saved = (
            session.query(Flashcard)
            .filter(Flashcard.deck_id == uuid.UUID(deck_id))
            .all()
        )

        assert len(saved) == first + second


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _NAMES, _NAMES)
def test_name_deck_once_property_keeps_the_first_name_it_was_given(
    owner: uuid.UUID, winning_name: str, later_name: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )

        untouched_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )

        assert name_deck_once(session, deck_id, winning_name)
        assert not name_deck_once(session, deck_id, later_name)

        deck = session.get(FlashcardDeck, uuid.UUID(deck_id))
        untouched = session.get(
            FlashcardDeck, uuid.UUID(untouched_id)
        )

        assert deck is not None
        assert deck.name == winning_name
        assert untouched is not None
        assert untouched.name == PENDING_NAME
