import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units.flashcard_router import (
    _deck_flashcards,
    _due_flashcards,
    _folder_flashcards,
)
from shared.models import Flashcard, FlashcardReview
from tests.property_support import property_world, seeded_deck
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_RATINGS = st.integers(min_value=1, max_value=4)
_CARD_COUNTS = st.integers(min_value=0, max_value=4)
_CLIENT, _SESSIONS = property_world()
_LATER = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=30)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _CARD_COUNTS, _CARD_COUNTS)
def test__deck_flashcards_property_counts_only_the_cards_that_are_due(
    owner: uuid.UUID, due_count: int, later_count: int
) -> None:
    with _SESSIONS() as session:
        _, deck_id, _ = seeded_deck(session, owner, due_count)
        _, later_deck, _ = seeded_deck(session, owner, later_count, _LATER)

        assert _deck_flashcards(session, deck_id).count() == due_count
        assert _deck_flashcards(session, later_deck).count() == 0


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _CARD_COUNTS)
def test__folder_flashcards_property_reaches_every_deck_in_the_folder(
    owner: uuid.UUID, due_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id, _, _ = seeded_deck(session, owner, due_count)
        found = _folder_flashcards(session, str(folder_id), str(owner))

        assert found.count() == due_count


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _CARD_COUNTS)
def test__due_flashcards_property_narrows_to_the_deck_when_one_is_named(
    owner: uuid.UUID, due_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id, deck_id, _ = seeded_deck(session, owner, due_count)
        by_deck = _due_flashcards(
            session, str(owner), str(deck_id), None
        )
        by_folder = _due_flashcards(
            session, str(owner), None, str(folder_id)
        )

        assert by_deck.count() == due_count
        assert by_folder.count() == due_count


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _CARD_COUNTS, st.integers(min_value=1, max_value=3))
def test_get_flashcards_property_never_returns_more_than_a_page(
    owner: uuid.UUID, due_count: int, per_page: int
) -> None:
    with _SESSIONS() as session:
        folder_id, _, _ = seeded_deck(session, owner, due_count)

    response = _CLIENT.get(
        "/flashcards",
        params={"folder_id": str(folder_id), "per_page": per_page},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, object]", response.json())
    returned = cast("list[object]", body["flashcards"])

    assert response.status_code == _OK
    assert body["total_flashcards"] == due_count
    assert len(returned) == min(per_page, due_count)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _RATINGS)
def test_review_flashcard_property_always_schedules_the_next_review(
    owner: uuid.UUID, rating: int
) -> None:
    with _SESSIONS() as session:
        _, _, card_ids = seeded_deck(session, owner, 1)

    response = _CLIENT.post(
        "/review-flashcard",
        json={"flashcard_id": card_ids[0], "rating": rating},
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        reviewed = session.get(Flashcard, card_ids[0])

        assert reviewed is not None
        assert reviewed.next_review is not None
        assert reviewed.fsrs_card is not None

    assert response.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _RATINGS)
def test__recorded_review_property_keeps_one_review_row_per_rating(
    owner: uuid.UUID, rating: int
) -> None:
    with _SESSIONS() as session:
        _, _, card_ids = seeded_deck(session, owner, 1)

    for _ in range(2):
        _ = _CLIENT.post(
            "/review-flashcard",
            json={"flashcard_id": card_ids[0], "rating": rating},
            headers=authorization(str(owner)),
        )

    with _SESSIONS() as session:
        recorded = (
            session.query(FlashcardReview)
            .filter(FlashcardReview.flashcard_id == card_ids[0])
            .count()
        )

    assert recorded == 2


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _RATINGS)
def test_review_flashcard_property_refuses_a_card_that_is_not_there(
    owner: uuid.UUID, rating: int
) -> None:
    response = _CLIENT.post(
        "/review-flashcard",
        json={"flashcard_id": 10_000_000, "rating": rating},
        headers=authorization(str(owner)),
    )

    assert response.status_code == _NOT_FOUND
