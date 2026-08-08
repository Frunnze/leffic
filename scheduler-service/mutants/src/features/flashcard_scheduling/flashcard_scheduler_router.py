from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fsrs.card import CardDict
from fsrs.scheduler import SchedulerDict
from pydantic import BaseModel

from features.flashcard_scheduling.flashcard_scheduler import (
    get_ratings_times,
    schedule_flashcard_fsrs,
)
from features.flashcard_scheduling.stored_scheduler import (
    scheduler_from_document,
)
from shared.claims_extractor import get_user_id_from_jwt
from shared.database import db

flashcard_scheduler = APIRouter()

_SCHEDULERS_COLLECTION = "schedulers_collection"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__stored_scheduler__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__stored_scheduler__mutmut)
def _stored_scheduler(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_orig(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_1(user_id: str) -> SchedulerDict | None:
    stored = None

    if not stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_2(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one(None)

    if not stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_3(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"XXuser_idXX": user_id})

    if not stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_4(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"USER_ID": user_id})

    if not stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_5(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if stored:
        return None

    return scheduler_from_document(stored)


def x__stored_scheduler__mutmut_6(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return scheduler_from_document(None)

mutants_x__stored_scheduler__mutmut['_mutmut_orig'] = x__stored_scheduler__mutmut_orig # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_1'] = x__stored_scheduler__mutmut_1 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_2'] = x__stored_scheduler__mutmut_2 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_3'] = x__stored_scheduler__mutmut_3 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_4'] = x__stored_scheduler__mutmut_4 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_5'] = x__stored_scheduler__mutmut_5 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_6'] = x__stored_scheduler__mutmut_6 # type: ignore # mutmut generated


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
