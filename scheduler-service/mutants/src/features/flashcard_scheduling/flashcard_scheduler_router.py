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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_mongo_row2dict__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_mongo_row2dict__mutmut)
def mongo_row2dict(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_orig(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_1(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = None
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_2(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(None, default=json_util.default)
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_3(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=None)
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_4(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(default=json_util.default)
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_5(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, )
    plain_document = cast("dict[str, object]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_6(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = None
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_7(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast(None, json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_8(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("dict[str, object]", None)
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_9(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast(json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_10(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("dict[str, object]", )
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_11(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("XXdict[str, object]XX", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_12(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("DICT[STR, OBJECT]", json.loads(result_json))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document


def x_mongo_row2dict__mutmut_13(mongo_result: MongoDocument) -> dict[str, object]:
    result_json = json.dumps(mongo_result, default=json_util.default)
    plain_document = cast("dict[str, object]", json.loads(None))
    del plain_document[_MONGO_ID_FIELD]

    return plain_document

mutants_x_mongo_row2dict__mutmut['_mutmut_orig'] = x_mongo_row2dict__mutmut_orig # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_1'] = x_mongo_row2dict__mutmut_1 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_2'] = x_mongo_row2dict__mutmut_2 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_3'] = x_mongo_row2dict__mutmut_3 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_4'] = x_mongo_row2dict__mutmut_4 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_5'] = x_mongo_row2dict__mutmut_5 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_6'] = x_mongo_row2dict__mutmut_6 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_7'] = x_mongo_row2dict__mutmut_7 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_8'] = x_mongo_row2dict__mutmut_8 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_9'] = x_mongo_row2dict__mutmut_9 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_10'] = x_mongo_row2dict__mutmut_10 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_11'] = x_mongo_row2dict__mutmut_11 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_12'] = x_mongo_row2dict__mutmut_12 # type: ignore # mutmut generated
mutants_x_mongo_row2dict__mutmut['x_mongo_row2dict__mutmut_13'] = x_mongo_row2dict__mutmut_13 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__stored_scheduler__mutmut)
def _stored_scheduler(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_orig(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_1(user_id: str) -> SchedulerDict | None:
    stored = None

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_2(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one(None)

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_3(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"XXuser_idXX": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_4(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"USER_ID": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_5(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_6(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast(None, cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_7(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", None)


def x__stored_scheduler__mutmut_8(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast(cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_9(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", )


def x__stored_scheduler__mutmut_10(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("XXSchedulerDictXX", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_11(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("schedulerdict", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_12(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SCHEDULERDICT", cast("object", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_13(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast(None, mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_14(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", None))


def x__stored_scheduler__mutmut_15(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast(mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_16(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", ))


def x__stored_scheduler__mutmut_17(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("XXobjectXX", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_18(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("OBJECT", mongo_row2dict(stored)))


def x__stored_scheduler__mutmut_19(user_id: str) -> SchedulerDict | None:
    stored = db[_SCHEDULERS_COLLECTION].find_one({"user_id": user_id})

    if not stored:
        return None

    return cast("SchedulerDict", cast("object", mongo_row2dict(None)))

mutants_x__stored_scheduler__mutmut['_mutmut_orig'] = x__stored_scheduler__mutmut_orig # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_1'] = x__stored_scheduler__mutmut_1 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_2'] = x__stored_scheduler__mutmut_2 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_3'] = x__stored_scheduler__mutmut_3 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_4'] = x__stored_scheduler__mutmut_4 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_5'] = x__stored_scheduler__mutmut_5 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_6'] = x__stored_scheduler__mutmut_6 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_7'] = x__stored_scheduler__mutmut_7 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_8'] = x__stored_scheduler__mutmut_8 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_9'] = x__stored_scheduler__mutmut_9 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_10'] = x__stored_scheduler__mutmut_10 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_11'] = x__stored_scheduler__mutmut_11 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_12'] = x__stored_scheduler__mutmut_12 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_13'] = x__stored_scheduler__mutmut_13 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_14'] = x__stored_scheduler__mutmut_14 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_15'] = x__stored_scheduler__mutmut_15 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_16'] = x__stored_scheduler__mutmut_16 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_17'] = x__stored_scheduler__mutmut_17 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_18'] = x__stored_scheduler__mutmut_18 # type: ignore # mutmut generated
mutants_x__stored_scheduler__mutmut['x__stored_scheduler__mutmut_19'] = x__stored_scheduler__mutmut_19 # type: ignore # mutmut generated


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
