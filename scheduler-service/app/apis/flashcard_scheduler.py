from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import traceback
from bson import json_util
import json
from pydantic import BaseModel
from typing import Optional

from .. import db
from ..tools.flashcard_scheduler import schedule_flashcard_fsrs


flashcard_scheduler = APIRouter()

def mongo_row2dict(mongo_result):
    result_json = json.dumps(mongo_result, default=json_util.default)
    d = json.loads(result_json)
    del d["_id"]
    return d


class ScheduleFlashcard(BaseModel):
    card: Optional[dict] = None
    rating: int
    user_id: str

@flashcard_scheduler.post("/schedule-flashcard")
async def schedule_flashcard(request_data: ScheduleFlashcard):
    try:
        # Get the card
        schedulers_collection = db["schedulers_collection"]
        scheduler = schedulers_collection.find_one({"user_id": request_data.user_id})
        if scheduler:
            scheduler = mongo_row2dict(scheduler)

        # Get and save the new card and the review log
        new_card, review_log, ratings_time = schedule_flashcard_fsrs(
            request_data.card, scheduler, request_data.rating
        )

        return JSONResponse(content={
            "new_card": new_card,
            "review_log": review_log,
            "ratings_time": ratings_time
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))