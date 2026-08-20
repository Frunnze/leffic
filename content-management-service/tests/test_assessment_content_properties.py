from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units.formatting import (
    _prepared_options,
    _prepared_true_false_content,
    _typed_accuracy,
    evaluate_accuracy,
)

_CORRECT = 1
_INCORRECT = 0
_CORRECT_OPTION_ID = 0
_LABELS = ["True", "False"]
_OPTION_TEXT = st.text(max_size=8)
_PADDING = st.sampled_from(["", " ", "\t", "  \n "])


def _options_of(
    prepared: dict[str, object],
) -> list[dict[str, object]]:
    return cast("list[dict[str, object]]", prepared["shuffled_options"])


@settings(max_examples=50)
@given(is_true=st.booleans(), statement=st.text(max_size=8))
def test__prepared_true_false_content_property_marks_the_truth_as_option_zero(
    *, is_true: bool, statement: str
) -> None:
    prepared = _prepared_true_false_content(
        {"is_true": is_true, "statement": statement}
    )
    options = _options_of(prepared)

    assert sorted(str(option["option"]) for option in options) == sorted(
        _LABELS
    )

    correct = next(
        option for option in options if option["id"] == _CORRECT_OPTION_ID
    )

    assert correct["option"] == ("True" if is_true else "False")


@settings(max_examples=50)
@given(_OPTION_TEXT, st.lists(_OPTION_TEXT, max_size=4))
def test__prepared_options_property_numbers_every_option_exactly_once(
    true_option: str, false_options: list[str]
) -> None:
    prepared = _prepared_options(
        {"true_option": true_option, "false_options": false_options}
    )
    options = _options_of(prepared)

    assert len(options) == len(false_options) + 1
    assert sorted(int(str(option["id"])) for option in options) == list(
        range(len(options))
    )

    correct = next(
        option for option in options if option["id"] == _CORRECT_OPTION_ID
    )

    assert correct["option"] == true_option


@settings(max_examples=50)
@given(
    st.integers(min_value=-3, max_value=5),
    st.sampled_from(["true_or_false", "multiple_choice", ""]),
)
def test_evaluate_accuracy_property_credits_only_the_first_option(
    answer: int, item_type: str
) -> None:
    scored = evaluate_accuracy([answer], item_type, {"answer": "ignored"})

    assert scored == (_CORRECT if answer == _CORRECT_OPTION_ID else _INCORRECT)


@settings(max_examples=50)
@given(st.text(min_size=1, max_size=10), _PADDING, _PADDING)
def test__typed_accuracy_property_ignores_case_and_surrounding_space(
    answer: str, before: str, after: str
) -> None:
    typed = f"{before}{answer.swapcase()}{after}"

    assert _typed_accuracy(typed, answer) == _CORRECT


@settings(max_examples=50)
@given(
    st.one_of(st.integers(), st.none(), st.lists(st.text(), max_size=2)),
    st.text(max_size=5),
)
def test__typed_accuracy_property_refuses_anything_that_is_not_text(
    typed: object, stored: str
) -> None:
    assert _typed_accuracy(typed, stored) == _INCORRECT
