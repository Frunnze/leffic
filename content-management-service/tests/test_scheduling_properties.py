from datetime import UTC, datetime
from typing import cast

from fsrs import Card, Scheduler
from fsrs.scheduler import SchedulerDict
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.flashcard_scheduling import (
    RATING_MAP,
    _restored_card,
    _restored_scheduler,
    get_ratings_times,
    schedule_flashcard_fsrs,
)

_RATINGS = st.integers(min_value=1, max_value=4)
_REVIEW_HISTORIES = st.lists(_RATINGS, max_size=4)


def _reviewed_card(ratings: list[int]) -> Card:
    scheduler = Scheduler()
    card = Card()

    for rating in ratings:
        card, _ = scheduler.review_card(card, RATING_MAP[rating])

    return card


@settings(max_examples=25)
@given(_REVIEW_HISTORIES)
def test__restored_card_property_round_trips_a_serialised_card(
    ratings: list[int],
) -> None:
    card = _reviewed_card(ratings)

    assert _restored_card(card.to_dict()).to_dict() == card.to_dict()


@settings(max_examples=25)
@given(st.sampled_from(cast("list[SchedulerDict | None]", [None, {}])))
def test__restored_scheduler_property_ignores_an_empty_scheduler(
    scheduler: SchedulerDict | None,
) -> None:
    restored = _restored_scheduler(scheduler)

    assert restored.to_dict() == Scheduler().to_dict()


@settings(max_examples=25, deadline=None)
@given(_REVIEW_HISTORIES, _RATINGS)
def test_schedule_flashcard_fsrs_property_never_schedules_into_the_past(
    ratings: list[int], rating: int
) -> None:
    reviewed_at = datetime.now(UTC)
    card, _ = schedule_flashcard_fsrs(
        _reviewed_card(ratings).to_dict(), None, rating
    )

    assert Card.from_dict(card).due >= reviewed_at


@settings(max_examples=25, deadline=None)
@given(_REVIEW_HISTORIES)
def test_get_ratings_times_property_never_returns_a_negative_wait(
    ratings: list[int],
) -> None:
    times = get_ratings_times(_reviewed_card(ratings).to_dict(), None)

    assert sorted(times) == [1, 2, 3, 4]
    assert all(seconds >= 0 for seconds in times.values())
