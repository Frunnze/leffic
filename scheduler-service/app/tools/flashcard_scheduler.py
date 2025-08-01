from fsrs import Scheduler, Card, Rating
from datetime import datetime, timezone
import copy

rating_map = {
    1: Rating.Again,
    2: Rating.Hard,
    3: Rating.Good,
    4: Rating.Easy
}

def schedule_flashcard_fsrs(card, scheduler, rating):
    timestamp = datetime.now(timezone.utc)

    if card:
        card = Card.from_dict(card)
    else:
        card = Card()

    if scheduler:
        scheduler = Scheduler.from_dict(scheduler)
    else:
        scheduler = Scheduler()

    rating_obj = rating_map[rating]
    new_card, review_log = scheduler.review_card(card, rating_obj)

    return new_card.to_dict(), review_log.to_dict()


def get_ratings_times(card, scheduler):
    timestamp = datetime.now(timezone.utc)

    if card:
        card = Card.from_dict(card)
    else:
        card = Card()

    if scheduler:
        scheduler = Scheduler.from_dict(scheduler)
    else:
        scheduler = Scheduler()

    ratings_times = {}
    for r, val in rating_map.items():
        temp_card = copy.deepcopy(card)
        scheduler = copy.deepcopy(scheduler)

        temp_card, _ = scheduler.review_card(temp_card, val)
        ratings_times[r] = max(0, int((temp_card.due - timestamp).total_seconds()))

    return ratings_times

# celery task
def optimize_scheduler(scheduler, user_id):
    new_scheduler = None

    # Check if there are enough review logs
    # ...

    # Get review logs
    # ...

    # Optimize the scheduler
    # ...

    return new_scheduler