from typing import TypeGuard

from fsrs.scheduler import SchedulerDict

from shared.database import MongoDocument

_MISSING_FIELD = "Stored scheduler is missing a field"


def scheduler_from_document(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def _is_object_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _floats(value: object) -> list[float]:
    if _is_object_list(value):
        return [_number(item) for item in value]

    raise TypeError(_MISSING_FIELD)


def _integers(value: object) -> list[int]:
    return [int(number) for number in _floats(value)]


def _number(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(_MISSING_FIELD)

    return float(value)


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise TypeError(_MISSING_FIELD)

    return value
