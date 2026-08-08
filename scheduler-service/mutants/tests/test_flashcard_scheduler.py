from datetime import UTC, datetime

from fsrs import Card, Scheduler
from fsrs.card import CardDict
from fsrs.scheduler import SchedulerDict

from features.flashcard_scheduling.flashcard_scheduler import (
    RATING_MAP,
    get_ratings_times,
    schedule_flashcard_fsrs,
)

_GOOD_RATING = 3
_AGAIN_RATING = 1
_EASY_RATING = 4
_A_LONG_WAIT = 600


def test_schedules_a_brand_new_card() -> None:
    new_card, review_log = schedule_flashcard_fsrs(None, None, _GOOD_RATING)

    assert "due" in new_card
    assert review_log["rating"] == _GOOD_RATING


def test_schedules_an_existing_card_with_an_existing_scheduler() -> None:
    card = Card().to_dict()
    scheduler = Scheduler().to_dict()

    new_card, _ = schedule_flashcard_fsrs(card, scheduler, _GOOD_RATING)

    assert new_card["card_id"] == card["card_id"]


def test_every_rating_gets_a_due_time() -> None:
    ratings_times = get_ratings_times(None, None)

    assert sorted(ratings_times) == sorted(RATING_MAP)


def test_due_times_are_never_negative() -> None:
    ratings_times = get_ratings_times(Card().to_dict(), Scheduler().to_dict())

    assert all(seconds >= 0 for seconds in ratings_times.values())


def test_harder_ratings_come_due_sooner_than_easier_ones() -> None:
    ratings_times = get_ratings_times(None, None)

    assert ratings_times[1] <= ratings_times[4]


def _scheduler_with_steps(seconds: int) -> SchedulerDict:
    stored = Scheduler().to_dict()
    stored["learning_steps"] = [seconds]

    return stored


def _seconds_until_due(card: CardDict) -> float:
    due = datetime.fromisoformat(str(card["due"]))

    return (due - datetime.now(UTC)).total_seconds()


def test_the_stored_scheduler_changes_the_schedule() -> None:
    quick_card, _ = schedule_flashcard_fsrs(
        None, _scheduler_with_steps(60), _AGAIN_RATING
    )
    slow_card, _ = schedule_flashcard_fsrs(
        None, _scheduler_with_steps(3600), _AGAIN_RATING
    )

    delay = _seconds_until_due(slow_card) - _seconds_until_due(quick_card)

    assert delay > _A_LONG_WAIT


def test_the_stored_scheduler_changes_the_rating_times() -> None:
    quick = get_ratings_times(None, _scheduler_with_steps(60))
    slow = get_ratings_times(None, _scheduler_with_steps(3600))

    assert quick[_AGAIN_RATING] < slow[_AGAIN_RATING]


def test_the_given_card_changes_the_rating_times() -> None:
    reviewed, _ = schedule_flashcard_fsrs(None, None, _EASY_RATING)
    reviewed, _ = schedule_flashcard_fsrs(reviewed, None, _EASY_RATING)

    reviewed_times = get_ratings_times(reviewed, None)
    new_times = get_ratings_times(None, None)

    assert reviewed_times[_GOOD_RATING] > new_times[_GOOD_RATING] * 2


def test_the_given_card_changes_the_schedule() -> None:
    reviewed, _ = schedule_flashcard_fsrs(None, None, _GOOD_RATING)
    twice, _ = schedule_flashcard_fsrs(reviewed, None, _GOOD_RATING)

    assert twice["due"] != reviewed["due"]
