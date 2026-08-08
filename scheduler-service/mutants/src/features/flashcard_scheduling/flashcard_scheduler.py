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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_schedule_flashcard_fsrs__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_schedule_flashcard_fsrs__mutmut)
def schedule_flashcard_fsrs(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        _restored_card(card), RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_orig(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        _restored_card(card), RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_1(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = None

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_2(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        None, RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_3(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        _restored_card(card), None
    )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_4(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_5(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        _restored_card(card), )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_6(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(None).review_card(
        _restored_card(card), RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()


def x_schedule_flashcard_fsrs__mutmut_7(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
    rating: int,
) -> tuple[CardDict, ReviewLogDict]:
    new_card, review_log = _restored_scheduler(scheduler).review_card(
        _restored_card(None), RATING_MAP[rating]
    )

    return new_card.to_dict(), review_log.to_dict()

mutants_x_schedule_flashcard_fsrs__mutmut['_mutmut_orig'] = x_schedule_flashcard_fsrs__mutmut_orig # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_1'] = x_schedule_flashcard_fsrs__mutmut_1 # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_2'] = x_schedule_flashcard_fsrs__mutmut_2 # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_3'] = x_schedule_flashcard_fsrs__mutmut_3 # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_4'] = x_schedule_flashcard_fsrs__mutmut_4 # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_5'] = x_schedule_flashcard_fsrs__mutmut_5 # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_6'] = x_schedule_flashcard_fsrs__mutmut_6 # type: ignore # mutmut generated
mutants_x_schedule_flashcard_fsrs__mutmut['x_schedule_flashcard_fsrs__mutmut_7'] = x_schedule_flashcard_fsrs__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_ratings_times__mutmut)
def get_ratings_times(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_orig(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_1(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = None
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_2(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(None)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_3(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = None
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_4(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(None)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_5(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = None
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_6(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(None)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_7(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = None

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_8(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = None
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_9(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            None, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_10(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, None
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_11(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_12(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_13(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = None
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_14(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due + timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_15(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = None

    return ratings_times


def x_get_ratings_times__mutmut_16(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            None, int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_17(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, None
        )

    return ratings_times


def x_get_ratings_times__mutmut_18(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            int(seconds_until_due)
        )

    return ratings_times


def x_get_ratings_times__mutmut_19(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, )

    return ratings_times


def x_get_ratings_times__mutmut_20(
    card: CardDict | None,
    scheduler: SchedulerDict | None,
) -> dict[int, int]:
    timestamp = datetime.now(UTC)
    restored_card = _restored_card(card)
    restored_scheduler = _restored_scheduler(scheduler)
    ratings_times: dict[int, int] = {}

    for rating_value, rating in RATING_MAP.items():
        reviewed_card, _ = restored_scheduler.review_card(
            restored_card, rating
        )
        seconds_until_due = (reviewed_card.due - timestamp).total_seconds()
        ratings_times[rating_value] = max(
            _NO_TIME_LEFT, int(None)
        )

    return ratings_times

mutants_x_get_ratings_times__mutmut['_mutmut_orig'] = x_get_ratings_times__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_1'] = x_get_ratings_times__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_2'] = x_get_ratings_times__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_3'] = x_get_ratings_times__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_4'] = x_get_ratings_times__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_5'] = x_get_ratings_times__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_6'] = x_get_ratings_times__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_7'] = x_get_ratings_times__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_8'] = x_get_ratings_times__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_9'] = x_get_ratings_times__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_10'] = x_get_ratings_times__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_11'] = x_get_ratings_times__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_12'] = x_get_ratings_times__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_13'] = x_get_ratings_times__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_14'] = x_get_ratings_times__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_15'] = x_get_ratings_times__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_16'] = x_get_ratings_times__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_17'] = x_get_ratings_times__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_18'] = x_get_ratings_times__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_19'] = x_get_ratings_times__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_ratings_times__mutmut['x_get_ratings_times__mutmut_20'] = x_get_ratings_times__mutmut_20 # type: ignore # mutmut generated
mutants_x__restored_card__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__restored_card__mutmut)
def _restored_card(card: CardDict | None) -> Card:
    if not card:
        return Card()

    return Card.from_dict(card)


def x__restored_card__mutmut_orig(card: CardDict | None) -> Card:
    if not card:
        return Card()

    return Card.from_dict(card)


def x__restored_card__mutmut_1(card: CardDict | None) -> Card:
    if card:
        return Card()

    return Card.from_dict(card)


def x__restored_card__mutmut_2(card: CardDict | None) -> Card:
    if not card:
        return Card()

    return Card.from_dict(None)

mutants_x__restored_card__mutmut['_mutmut_orig'] = x__restored_card__mutmut_orig # type: ignore # mutmut generated
mutants_x__restored_card__mutmut['x__restored_card__mutmut_1'] = x__restored_card__mutmut_1 # type: ignore # mutmut generated
mutants_x__restored_card__mutmut['x__restored_card__mutmut_2'] = x__restored_card__mutmut_2 # type: ignore # mutmut generated
mutants_x__restored_scheduler__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__restored_scheduler__mutmut)
def _restored_scheduler(scheduler: SchedulerDict | None) -> Scheduler:
    if not scheduler:
        return Scheduler()

    return Scheduler.from_dict(scheduler)


def x__restored_scheduler__mutmut_orig(scheduler: SchedulerDict | None) -> Scheduler:
    if not scheduler:
        return Scheduler()

    return Scheduler.from_dict(scheduler)


def x__restored_scheduler__mutmut_1(scheduler: SchedulerDict | None) -> Scheduler:
    if scheduler:
        return Scheduler()

    return Scheduler.from_dict(scheduler)


def x__restored_scheduler__mutmut_2(scheduler: SchedulerDict | None) -> Scheduler:
    if not scheduler:
        return Scheduler()

    return Scheduler.from_dict(None)

mutants_x__restored_scheduler__mutmut['_mutmut_orig'] = x__restored_scheduler__mutmut_orig # type: ignore # mutmut generated
mutants_x__restored_scheduler__mutmut['x__restored_scheduler__mutmut_1'] = x__restored_scheduler__mutmut_1 # type: ignore # mutmut generated
mutants_x__restored_scheduler__mutmut['x__restored_scheduler__mutmut_2'] = x__restored_scheduler__mutmut_2 # type: ignore # mutmut generated
