from fsrs import Scheduler, Card, Rating
from datetime import datetime, timezone


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

    # Ratings time for future review
    future_ratings_time = get_ratings_time(new_card, scheduler, timestamp)

    return new_card.to_dict(), review_log.to_dict(), future_ratings_time


def get_ratings_time(card, scheduler, timestamp):
    ratings_time = {}
    for r, val in rating_map.items():
        temp_card, _ = scheduler.review_card(card, val)
        time_delta = temp_card.due - timestamp
        ratings_time[r] = time_delta.seconds
    
    return ratings_time