import uuid
from typing import cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import (
    MissingFolderError,
    _cards_of,
    _existing_folder,
    save_flashcard_deck,
    save_note,
    save_test,
)
from shared.models import Flashcard, Note, TestItem
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_MISSING_FOLDER = "Folder does not exist!"
_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)
_CARD = st.fixed_dictionaries({"front": st.text(max_size=6)})
_CARD_GROUPS = st.dictionaries(
    st.sampled_from(["basic_flashcards", "cloze_flashcards"]),
    st.lists(_CARD, max_size=3),
    max_size=2,
)
_ITEM_GROUPS = st.dictionaries(
    st.sampled_from(["multiple_choice_test_items", "short_answer_test_items"]),
    st.lists(_CARD, max_size=3),
    max_size=2,
)


@settings(max_examples=50)
@given(
    st.one_of(
        st.lists(st.one_of(_CARD, st.integers(), st.none()), max_size=5),
        st.text(max_size=5),
        st.integers(),
        st.none(),
    )
)
def test__cards_of_property_keeps_exactly_the_mappings(
    cards: object,
) -> None:
    kept = _cards_of(cards)

    if isinstance(cards, list):
        assert kept == [
            card
            for card in cast("list[object]", cards)
            if isinstance(card, dict)
        ]
    else:
        assert kept == []


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test__existing_folder_property_refuses_a_folder_that_is_not_there(
    owner: uuid.UUID, absent: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        assert _existing_folder(session, str(folder_id)).id == folder_id

        with pytest.raises(MissingFolderError, match=_MISSING_FOLDER):
            _ = _existing_folder(session, str(absent))


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _CARD_GROUPS)
def test_save_flashcard_deck_property_saves_every_card_it_was_given(
    owner: uuid.UUID, groups: dict[str, list[dict[str, str]]]
) -> None:
    expected = sum(len(cards) for cards in groups.values())

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = save_flashcard_deck(
            session, str(folder_id), "Deck", groups, _NO_SOURCE
        )
        saved = (
            session.query(Flashcard)
            .filter(Flashcard.deck_id == uuid.UUID(deck_id))
            .all()
        )

    assert len(saved) == expected
    assert all("_flashcards" not in card.type for card in saved)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.text(max_size=12), st.text(max_size=20))
def test_save_note_property_round_trips_the_name_and_the_body(
    owner: uuid.UUID, name: str, body: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        note_id = save_note(
            session, str(folder_id), name, body, _NO_SOURCE
        )
        saved = session.get(Note, uuid.UUID(note_id))

        assert saved is not None
        assert saved.name == name
        assert saved.content == body


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_GROUPS)
def test_save_test_property_saves_every_item_it_was_given(
    owner: uuid.UUID, groups: dict[str, list[dict[str, str]]]
) -> None:
    expected = sum(len(items) for items in groups.values())

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = save_test(
            session, str(folder_id), "Test", groups, _NO_SOURCE
        )
        saved = (
            session.query(TestItem)
            .filter(TestItem.test_id == uuid.UUID(test_id))
            .all()
        )

    assert len(saved) == expected
    assert all("_test_items" not in item.type for item in saved)


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=3))
def test___init___property_always_names_the_missing_folder(
    count: int,
) -> None:
    errors = [MissingFolderError() for _ in range(count)]

    assert all(str(error) == _MISSING_FOLDER for error in errors)
