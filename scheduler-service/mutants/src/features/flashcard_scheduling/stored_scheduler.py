from typing import TypeGuard

from fsrs.scheduler import SchedulerDict

from shared.database import MongoDocument

_MISSING_FIELD = "Stored scheduler is missing a field"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_scheduler_from_document__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_scheduler_from_document__mutmut)
def scheduler_from_document(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_orig(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_1(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=None,
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_2(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=None,
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_3(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=None,
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_4(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=None,
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_5(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=None,
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_6(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=None,
    )


def x_scheduler_from_document__mutmut_7(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_8(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_9(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_10(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_11(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_12(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        )


def x_scheduler_from_document__mutmut_13(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(None),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_14(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get(None)),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_15(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("XXparametersXX")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_16(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("PARAMETERS")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_17(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(None),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_18(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get(None)),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_19(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("XXdesired_retentionXX")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_20(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("DESIRED_RETENTION")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_21(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(None),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_22(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get(None)),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_23(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("XXlearning_stepsXX")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_24(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("LEARNING_STEPS")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_25(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(None),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_26(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get(None)),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_27(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("XXrelearning_stepsXX")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_28(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("RELEARNING_STEPS")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_29(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(None),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_30(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(None)),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_31(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get(None))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_32(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("XXmaximum_intervalXX"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_33(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("MAXIMUM_INTERVAL"))),
        enable_fuzzing=_flag(document.get("enable_fuzzing")),
    )


def x_scheduler_from_document__mutmut_34(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(None),
    )


def x_scheduler_from_document__mutmut_35(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get(None)),
    )


def x_scheduler_from_document__mutmut_36(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("XXenable_fuzzingXX")),
    )


def x_scheduler_from_document__mutmut_37(document: MongoDocument) -> SchedulerDict:
    return SchedulerDict(
        parameters=_floats(document.get("parameters")),
        desired_retention=_number(document.get("desired_retention")),
        learning_steps=_integers(document.get("learning_steps")),
        relearning_steps=_integers(document.get("relearning_steps")),
        maximum_interval=int(_number(document.get("maximum_interval"))),
        enable_fuzzing=_flag(document.get("ENABLE_FUZZING")),
    )

mutants_x_scheduler_from_document__mutmut['_mutmut_orig'] = x_scheduler_from_document__mutmut_orig # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_1'] = x_scheduler_from_document__mutmut_1 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_2'] = x_scheduler_from_document__mutmut_2 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_3'] = x_scheduler_from_document__mutmut_3 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_4'] = x_scheduler_from_document__mutmut_4 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_5'] = x_scheduler_from_document__mutmut_5 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_6'] = x_scheduler_from_document__mutmut_6 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_7'] = x_scheduler_from_document__mutmut_7 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_8'] = x_scheduler_from_document__mutmut_8 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_9'] = x_scheduler_from_document__mutmut_9 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_10'] = x_scheduler_from_document__mutmut_10 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_11'] = x_scheduler_from_document__mutmut_11 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_12'] = x_scheduler_from_document__mutmut_12 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_13'] = x_scheduler_from_document__mutmut_13 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_14'] = x_scheduler_from_document__mutmut_14 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_15'] = x_scheduler_from_document__mutmut_15 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_16'] = x_scheduler_from_document__mutmut_16 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_17'] = x_scheduler_from_document__mutmut_17 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_18'] = x_scheduler_from_document__mutmut_18 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_19'] = x_scheduler_from_document__mutmut_19 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_20'] = x_scheduler_from_document__mutmut_20 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_21'] = x_scheduler_from_document__mutmut_21 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_22'] = x_scheduler_from_document__mutmut_22 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_23'] = x_scheduler_from_document__mutmut_23 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_24'] = x_scheduler_from_document__mutmut_24 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_25'] = x_scheduler_from_document__mutmut_25 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_26'] = x_scheduler_from_document__mutmut_26 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_27'] = x_scheduler_from_document__mutmut_27 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_28'] = x_scheduler_from_document__mutmut_28 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_29'] = x_scheduler_from_document__mutmut_29 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_30'] = x_scheduler_from_document__mutmut_30 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_31'] = x_scheduler_from_document__mutmut_31 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_32'] = x_scheduler_from_document__mutmut_32 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_33'] = x_scheduler_from_document__mutmut_33 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_34'] = x_scheduler_from_document__mutmut_34 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_35'] = x_scheduler_from_document__mutmut_35 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_36'] = x_scheduler_from_document__mutmut_36 # type: ignore # mutmut generated
mutants_x_scheduler_from_document__mutmut['x_scheduler_from_document__mutmut_37'] = x_scheduler_from_document__mutmut_37 # type: ignore # mutmut generated


def _is_object_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)
mutants_x__floats__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__floats__mutmut)
def _floats(value: object) -> list[float]:
    if _is_object_list(value):
        return [_number(item) for item in value]

    raise TypeError(_MISSING_FIELD)


def x__floats__mutmut_orig(value: object) -> list[float]:
    if _is_object_list(value):
        return [_number(item) for item in value]

    raise TypeError(_MISSING_FIELD)


def x__floats__mutmut_1(value: object) -> list[float]:
    if _is_object_list(None):
        return [_number(item) for item in value]

    raise TypeError(_MISSING_FIELD)


def x__floats__mutmut_2(value: object) -> list[float]:
    if _is_object_list(value):
        return [_number(None) for item in value]

    raise TypeError(_MISSING_FIELD)


def x__floats__mutmut_3(value: object) -> list[float]:
    if _is_object_list(value):
        return [_number(item) for item in value]

    raise TypeError(None)

mutants_x__floats__mutmut['_mutmut_orig'] = x__floats__mutmut_orig # type: ignore # mutmut generated
mutants_x__floats__mutmut['x__floats__mutmut_1'] = x__floats__mutmut_1 # type: ignore # mutmut generated
mutants_x__floats__mutmut['x__floats__mutmut_2'] = x__floats__mutmut_2 # type: ignore # mutmut generated
mutants_x__floats__mutmut['x__floats__mutmut_3'] = x__floats__mutmut_3 # type: ignore # mutmut generated
mutants_x__integers__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__integers__mutmut)
def _integers(value: object) -> list[int]:
    return [int(number) for number in _floats(value)]


def x__integers__mutmut_orig(value: object) -> list[int]:
    return [int(number) for number in _floats(value)]


def x__integers__mutmut_1(value: object) -> list[int]:
    return [int(None) for number in _floats(value)]


def x__integers__mutmut_2(value: object) -> list[int]:
    return [int(number) for number in _floats(None)]

mutants_x__integers__mutmut['_mutmut_orig'] = x__integers__mutmut_orig # type: ignore # mutmut generated
mutants_x__integers__mutmut['x__integers__mutmut_1'] = x__integers__mutmut_1 # type: ignore # mutmut generated
mutants_x__integers__mutmut['x__integers__mutmut_2'] = x__integers__mutmut_2 # type: ignore # mutmut generated
mutants_x__number__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__number__mutmut)
def _number(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(_MISSING_FIELD)

    return float(value)


def x__number__mutmut_orig(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(_MISSING_FIELD)

    return float(value)


def x__number__mutmut_1(value: object) -> float:
    if isinstance(value, (int, float)):
        raise TypeError(_MISSING_FIELD)

    return float(value)


def x__number__mutmut_2(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(None)

    return float(value)


def x__number__mutmut_3(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(_MISSING_FIELD)

    return float(None)

mutants_x__number__mutmut['_mutmut_orig'] = x__number__mutmut_orig # type: ignore # mutmut generated
mutants_x__number__mutmut['x__number__mutmut_1'] = x__number__mutmut_1 # type: ignore # mutmut generated
mutants_x__number__mutmut['x__number__mutmut_2'] = x__number__mutmut_2 # type: ignore # mutmut generated
mutants_x__number__mutmut['x__number__mutmut_3'] = x__number__mutmut_3 # type: ignore # mutmut generated
mutants_x__flag__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__flag__mutmut)
def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise TypeError(_MISSING_FIELD)

    return value


def x__flag__mutmut_orig(value: object) -> bool:
    if not isinstance(value, bool):
        raise TypeError(_MISSING_FIELD)

    return value


def x__flag__mutmut_1(value: object) -> bool:
    if isinstance(value, bool):
        raise TypeError(_MISSING_FIELD)

    return value


def x__flag__mutmut_2(value: object) -> bool:
    if not isinstance(value, bool):
        raise TypeError(None)

    return value

mutants_x__flag__mutmut['_mutmut_orig'] = x__flag__mutmut_orig # type: ignore # mutmut generated
mutants_x__flag__mutmut['x__flag__mutmut_1'] = x__flag__mutmut_1 # type: ignore # mutmut generated
mutants_x__flag__mutmut['x__flag__mutmut_2'] = x__flag__mutmut_2 # type: ignore # mutmut generated
