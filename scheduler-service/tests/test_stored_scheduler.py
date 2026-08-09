import pytest
from fsrs import Scheduler

from features.flashcard_scheduling.stored_scheduler import (
    scheduler_from_document,
)
from shared.database import MongoDocument


def _document(**overrides: object) -> MongoDocument:
    document: MongoDocument = dict(Scheduler().to_dict())
    document["_id"] = "mongo-id"
    document["user_id"] = "someone"
    document.update(overrides)

    return document


def test_reads_every_scheduler_field() -> None:
    stored = scheduler_from_document(_document())
    expected = Scheduler().to_dict()

    assert stored["desired_retention"] == expected["desired_retention"]
    assert stored["maximum_interval"] == expected["maximum_interval"]
    assert stored["enable_fuzzing"] == expected["enable_fuzzing"]


def test_drops_fields_mongo_added() -> None:
    stored = scheduler_from_document(_document())

    assert "_id" not in stored
    assert "user_id" not in stored


def test_keeps_the_stored_retention() -> None:
    stored = scheduler_from_document(_document(desired_retention=0.75))

    assert stored["desired_retention"] == 0.75


def test_keeps_the_stored_interval() -> None:
    stored = scheduler_from_document(_document(maximum_interval=99))

    assert stored["maximum_interval"] == 99


def test_keeps_the_stored_fuzzing_flag() -> None:
    stored = scheduler_from_document(_document(enable_fuzzing=False))

    assert stored["enable_fuzzing"] is False


def test_keeps_the_stored_parameters() -> None:
    stored = scheduler_from_document(_document(parameters=[0.5, 1.5]))

    assert stored["parameters"] == [0.5, 1.5]


def test_learning_steps_become_whole_numbers() -> None:
    stored = scheduler_from_document(_document(learning_steps=[1.0, 10.0]))

    assert stored["learning_steps"] == [1, 10]


def test_relearning_steps_become_whole_numbers() -> None:
    stored = scheduler_from_document(_document(relearning_steps=[7.0]))

    assert stored["relearning_steps"] == [7]


def test_rejects_parameters_that_are_not_a_list() -> None:
    with pytest.raises(TypeError, match="missing a field"):
        _ = scheduler_from_document(_document(parameters="nope"))


def test_rejects_a_retention_that_is_not_a_number() -> None:
    with pytest.raises(TypeError, match="missing a field"):
        _ = scheduler_from_document(_document(desired_retention="nope"))


def test_rejects_a_fuzzing_flag_that_is_not_a_boolean() -> None:
    with pytest.raises(TypeError, match="missing a field"):
        _ = scheduler_from_document(_document(enable_fuzzing="yes"))


def test_rejects_a_parameter_that_is_not_a_number() -> None:
    with pytest.raises(TypeError, match="missing a field"):
        _ = scheduler_from_document(_document(parameters=["nope"]))
