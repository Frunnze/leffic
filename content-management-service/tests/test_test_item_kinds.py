from typing import cast

import pytest

from features.study_units.formatting import (
    evaluate_accuracy,
    prepare_content,
)
from shared.models import TestItem

_MULTIPLE_CHOICE: dict[str, object] = {
    "question": "Which sea did Athens dominate?",
    "true_option": "The Aegean",
    "false_options": ["The Baltic", "The Red Sea"],
}
_TRUE_OR_FALSE: dict[str, object] = {
    "statement": "Sparta was ruled by two kings.",
    "is_true": True,
}
_SHORT_ANSWER: dict[str, object] = {
    "question": "Which sea did Athens dominate?",
    "answer": "The Aegean",
}
_MULTIPLE_CHOICE_OPTION_COUNT = 3


@pytest.fixture
def short_answer_item() -> TestItem:
    return TestItem(type="short_answer", content=_SHORT_ANSWER)


def _options(prepared: dict[str, object]) -> list[dict[str, object]]:
    return cast("list[dict[str, object]]", prepared["shuffled_options"])


def test_a_true_or_false_item_ids_both_answers() -> None:
    prepared = prepare_content(_TRUE_OR_FALSE, "true_or_false")
    by_id = {
        int(str(option["id"])): option["option"]
        for option in _options(prepared)
    }

    assert by_id == {0: "True", 1: "False"}


def test_a_true_or_false_item_asks_the_statement() -> None:
    prepared = prepare_content(_TRUE_OR_FALSE, "true_or_false")

    assert prepared["question"] == "Sparta was ruled by two kings."


def test_the_answer_matching_the_statement_is_the_correct_option() -> None:
    prepared = prepare_content(_TRUE_OR_FALSE, "true_or_false")
    correct = next(
        option for option in _options(prepared) if option["id"] == 0
    )

    assert correct["option"] == "True"


def test_a_false_statement_makes_false_the_correct_option() -> None:
    statement: dict[str, object] = {
        "statement": "Sparta had no army.",
        "is_true": False,
    }
    prepared = prepare_content(statement, "true_or_false")
    by_id = {
        int(str(option["id"])): option["option"]
        for option in _options(prepared)
    }

    assert by_id == {0: "False", 1: "True"}


def test_a_short_answer_item_offers_no_options() -> None:
    prepared = prepare_content(_SHORT_ANSWER, "short_answer")

    assert _options(prepared) == []


def test_a_short_answer_item_keeps_its_question() -> None:
    prepared = prepare_content(_SHORT_ANSWER, "short_answer")

    assert prepared["question"] == "Which sea did Athens dominate?"


def test_multiple_choice_still_shuffles_every_option() -> None:
    prepared = prepare_content(_MULTIPLE_CHOICE, "multiple_choice")

    assert len(_options(prepared)) == _MULTIPLE_CHOICE_OPTION_COUNT


def test_a_legacy_multiple_choice_type_is_still_understood() -> None:
    prepared = prepare_content(_MULTIPLE_CHOICE, "mult_choice")

    assert len(_options(prepared)) == _MULTIPLE_CHOICE_OPTION_COUNT


@pytest.mark.parametrize(
    "typed",
    ["The Aegean", "the aegean", "  The Aegean  "],
)
def test_a_short_answer_matching_the_stored_answer_is_correct(
    typed: str,
) -> None:
    accuracy = evaluate_accuracy([typed], "short_answer", _SHORT_ANSWER)

    assert accuracy == 1


@pytest.mark.parametrize("typed", ["The Baltic", "", "Aegean sea"])
def test_a_short_answer_that_differs_is_incorrect(typed: str) -> None:
    accuracy = evaluate_accuracy([typed], "short_answer", _SHORT_ANSWER)

    assert accuracy == 0


def test_a_chosen_correct_option_is_still_correct() -> None:
    accuracy = evaluate_accuracy([0], "multiple_choice", _MULTIPLE_CHOICE)

    assert accuracy == 1


def test_a_chosen_wrong_option_is_still_incorrect() -> None:
    accuracy = evaluate_accuracy([2], "multiple_choice", _MULTIPLE_CHOICE)

    assert accuracy == 0


def test_a_short_answer_item_without_a_stored_answer_is_incorrect() -> None:
    accuracy = evaluate_accuracy(["anything"], "short_answer", {})

    assert accuracy == 0


def test_a_short_answer_item_is_graded_on_its_text(
    short_answer_item: TestItem,
) -> None:
    accuracy = evaluate_accuracy(
        ["The Aegean"], short_answer_item.type, short_answer_item.content
    )

    assert accuracy == 1


def test_a_wrong_short_answer_is_graded_as_incorrect(
    short_answer_item: TestItem,
) -> None:
    accuracy = evaluate_accuracy(
        ["The Baltic"], short_answer_item.type, short_answer_item.content
    )

    assert accuracy == 0


def test_an_option_item_is_graded_on_its_chosen_option() -> None:
    item = TestItem(type="multiple_choice", content=_MULTIPLE_CHOICE)

    assert evaluate_accuracy([0], item.type, item.content) == 1
    assert evaluate_accuracy([1], item.type, item.content) == 0
