import json
from typing import Annotated, cast

from bson import json_util
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fsrs.card import CardDict
from fsrs.scheduler import SchedulerDict
from pydantic import BaseModel

from features.flashcard_scheduling.flashcard_scheduler import (
    get_ratings_times,
    schedule_flashcard_fsrs,
)
from shared.claims_extractor import get_user_id_from_jwt
from shared.database import MongoDocument, db

flashcard_scheduler = APIRouter()

_SCHEDULERS_COLLECTION = "schedulers_collection"
_MONGO_ID_FIELD = "_id"


def mongo_row2dict(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def _stored_scheduler(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


class ScheduleFlashcard(BaseModel):
    card: CardDict | None = None
    rating: int
    user_id: str


@flashcard_scheduler.post("/schedule-flashcard")
async def schedule_flashcard(request_data: ScheduleFlashcard) -> JSONResponse:
    # Get the card
    scheduler = _stored_scheduler(request_data.user_id)

    # Get and save the new card and the review log
    new_card, review_log = schedule_flashcard_fsrs(
        request_data.card, scheduler, request_data.rating
    )

    return JSONResponse(
        content={"new_card": new_card, "review_log": review_log}
    )


class RatingsTimesReq(BaseModel):
    card: CardDict | None = None


@flashcard_scheduler.post("/ratings-times")
async def ratings_times(
    req_data: RatingsTimesReq,
    user_id: Annotated[str, Depends(get_user_id_from_jwt)],
) -> JSONResponse:
    scheduler = _stored_scheduler(user_id)

    return JSONResponse(content=get_ratings_times(req_data.card, scheduler))
