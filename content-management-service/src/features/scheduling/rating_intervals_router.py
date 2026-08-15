from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fsrs.card import CardDict
from pydantic import BaseModel

from shared.dependencies import AuthenticatedUserId
from shared.flashcard_scheduling import (
    UnreadableCardError,
    get_ratings_times,
)

rating_intervals_router = APIRouter()


class RatingIntervalsRequest(BaseModel):
    card: CardDict | None = None


@rating_intervals_router.post("/rating-intervals")
async def rating_intervals(
    request_data: RatingIntervalsRequest, user_id: AuthenticatedUserId
) -> JSONResponse:
    _ = user_id

    try:
        intervals = get_ratings_times(request_data.card, None)
    except UnreadableCardError as unreadable:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(unreadable),
        ) from unreadable

    return JSONResponse(content=intervals)
