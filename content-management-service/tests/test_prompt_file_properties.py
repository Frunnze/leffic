import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.prompts.prompt_file import (
    MissingPromptFileError,
    assessment_item_values,
    flashcard_values,
    rendered_prompt,
)
from tests.prompt_catalog import every_prompt_file

_LEVELS = st.sampled_from(["high", "medium", "low"])
_AMOUNTS = st.one_of(st.none(), st.integers(min_value=1, max_value=99))
_PROMPT_FILES = st.sampled_from(every_prompt_file())


@settings(max_examples=50)
@given(_PROMPT_FILES, _LEVELS, _LEVELS, _AMOUNTS)
def test_rendered_prompt_property_leaves_no_placeholder_behind(
    prompt_file: str,
    comprehensiveness: str,
    verbosity: str,
    amount: int | None,
) -> None:
    values = flashcard_values(comprehensiveness, verbosity, amount)
    values.update(assessment_item_values(amount))

    assert "$" not in rendered_prompt(prompt_file, values)


@settings(max_examples=50)
@given(_PROMPT_FILES, _LEVELS, _LEVELS, _AMOUNTS)
def test_rendered_prompt_property_always_asks_for_the_extracted_text(
    prompt_file: str,
    comprehensiveness: str,
    verbosity: str,
    amount: int | None,
) -> None:
    values = flashcard_values(comprehensiveness, verbosity, amount)
    values.update(assessment_item_values(amount))
    rendered = rendered_prompt(prompt_file, values)

    assert "## Role" in rendered
    assert rendered.rstrip().endswith("## Extracted text")


@settings(max_examples=25)
@given(st.text(min_size=1, max_size=12))
def test_rendered_prompt_property_refuses_a_prompt_file_that_is_absent(
    name: str,
) -> None:
    if name in every_prompt_file():
        return

    with pytest.raises(MissingPromptFileError) as refused:
        _ = rendered_prompt(name, {})

    assert str(refused.value) == f"No prompt file named {name}.md"


@settings(max_examples=50)
@given(_LEVELS, _LEVELS, _AMOUNTS)
def test_flashcard_values_property_carries_the_settings_it_was_given(
    comprehensiveness: str, verbosity: str, amount: int | None
) -> None:
    values = flashcard_values(comprehensiveness, verbosity, amount)

    assert values["comprehensiveness"] == comprehensiveness
    assert values["verbosity"] == verbosity

    if amount is None:
        assert values["amount_constraint"] == ""
    else:
        assert (
            values["amount_constraint"]
            == f"- Flashcards number: {amount};"
        )


@settings(max_examples=50)
@given(_AMOUNTS)
def test_assessment_item_values_property_states_the_amount_when_given(
    amount: int | None,
) -> None:
    constraint = assessment_item_values(amount)["amount_constraint"]

    if amount is None:
        assert constraint == ""
    else:
        assert constraint == f"- Test items number: {amount};"
