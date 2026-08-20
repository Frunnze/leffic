import pytest

from features.study_units_generation.prompts.prompt_file import (
    assessment_item_values,
    flashcard_values,
    rendered_prompt,
)
from features.study_units_generation.study_unit_types import (
    NOTE_PROMPT_FILE,
    study_unit_type,
)
from tests.prompt_catalog import every_prompt_file

_FLASHCARD_TYPES = ("basic", "cloze", "feynman", "list")
_ITEM_TYPES = ("multiple_choice", "true_or_false", "short_answer")


def _flashcard_prompt(
    flashcard_type: str,
    comprehensiveness: str = "medium",
    verbosity: str = "low",
    amount: int | None = None,
) -> str:
    return rendered_prompt(
        study_unit_type(flashcard_type).prompt_file,
        flashcard_values(comprehensiveness, verbosity, amount),
    )


@pytest.mark.parametrize("flashcard_type", _FLASHCARD_TYPES)
def test_only_the_requested_card_type_is_described(
    flashcard_type: str,
) -> None:
    prompt = _flashcard_prompt(flashcard_type)
    others = [
        other for other in _FLASHCARD_TYPES if other != flashcard_type
    ]

    assert f"{flashcard_type}_flashcards" in prompt
    assert all(f"{other}_flashcards" not in prompt for other in others)


@pytest.mark.parametrize("flashcard_type", _FLASHCARD_TYPES)
def test_every_card_prompt_asks_for_a_deck_name(
    flashcard_type: str,
) -> None:
    assert '"deck_name"' in _flashcard_prompt(flashcard_type)


def test_flashcards_prompt_carries_the_requested_settings() -> None:
    prompt = _flashcard_prompt("basic", "high", "high")

    assert "Comprehensiveness: high" in prompt
    assert "Flashcard verbosity: high" in prompt


def test_flashcards_prompt_states_the_amount_when_given() -> None:
    assert "Flashcards number: 12" in _flashcard_prompt(
        "basic", amount=12
    )


def test_no_amount_leaves_the_constraint_line_empty() -> None:
    prompt = _flashcard_prompt("basic")
    block = prompt.split("## Constraints")[1].split("## Output format")[0]
    lines = [line.strip() for line in block.splitlines() if line.strip()]

    assert lines == [
        "- Comprehensiveness: medium;",
        "- Flashcard verbosity: low;",
    ]


def test_notes_prompt_asks_for_the_note_fields() -> None:
    prompt = rendered_prompt(NOTE_PROMPT_FILE, {})

    assert "note_content" in prompt
    assert "note_name" in prompt


def test_test_prompt_asks_for_multiple_choice_items() -> None:
    prompt = rendered_prompt(
        study_unit_type("multiple_choice").prompt_file,
        assessment_item_values(10),
    )

    assert "multiple_choice_test_items" in prompt
    assert "test_name" in prompt


@pytest.mark.parametrize("item_type", _ITEM_TYPES)
def test_every_item_prompt_states_the_amount_when_given(
    item_type: str,
) -> None:
    prompt = rendered_prompt(
        study_unit_type(item_type).prompt_file, assessment_item_values(7)
    )

    assert "Test items number: 7" in prompt


@pytest.mark.parametrize("prompt_file", every_prompt_file())
def test_the_output_format_is_a_json_object(prompt_file: str) -> None:
    values = flashcard_values("medium", "low", None)
    values.update(assessment_item_values(None))
    prompt = rendered_prompt(prompt_file, values)
    body = prompt.split("JSON```")[1].split("```")[0].strip()

    assert body.startswith("{")
    assert body.endswith("}")


@pytest.mark.parametrize("prompt_file", every_prompt_file())
def test_every_prompt_ends_by_handing_over_the_material(
    prompt_file: str,
) -> None:
    values = flashcard_values("medium", "low", None)
    values.update(assessment_item_values(None))
    prompt = rendered_prompt(prompt_file, values)

    assert prompt.startswith("## Role")
    assert prompt.rstrip().endswith("## Extracted text")
