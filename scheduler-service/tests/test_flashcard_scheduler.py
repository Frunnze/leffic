from fsrs import Card, Scheduler

from src.features.flashcard_scheduling.flashcard_scheduler import (
    RATING_MAP,
    get_ratings_times,
    schedule_flashcard_fsrs,
)

_GOOD_RATING = 3


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
