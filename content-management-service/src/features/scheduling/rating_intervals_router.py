from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fsrs.card import CardDict
from pydantic import BaseModel

from features.scheduling.flashcard_scheduling import get_ratings_times
from shared.dependencies import AuthenticatedUserId

rating_intervals_router = APIRouter()


class RatingIntervalsRequest(BaseModel):
    card: CardDict | None = None


@rating_intervals_router.post("/rating-intervals")
async def rating_intervals(
    request_data: RatingIntervalsRequest, user_id: AuthenticatedUserId
) -> JSONResponse:
    _ = user_id

    return JSONResponse(content=get_ratings_times(request_data.card, None))
