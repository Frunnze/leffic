import copy
from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler
from fsrs.card import CardDict
from fsrs.review_log import ReviewLogDict
from fsrs.scheduler import SchedulerDict

RATING_MAP: dict[int, Rating] = {
    1: Rating.Again,
    2: Rating.Hard,
    3: Rating.Good,
    4: Rating.Easy,
}

_NO_TIME_LEFT = 0


def schedule_flashcard_fsrs(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        _restored_card(card), RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()


def get_ratings_times(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = copy.deepcopy(restored_scheduler).review_card(
            copy.deepcopy(restored_card), rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def _restored_card(card: CardDict | None) -> Card:
    if not card:
        return Card()

    return Card.from_dict(card)


def _restored_scheduler(scheduler: SchedulerDict | None) -> Scheduler:
    if not scheduler:
        return Scheduler()

    return Scheduler.from_dict(scheduler)
