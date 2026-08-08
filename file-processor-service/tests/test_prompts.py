from features.study_units_generation.prompts.flashcards_prompt import (
    get_flashcards_system_prompt,
)
from features.study_units_generation.prompts.notes_prompt import (
    get_notes_system_prompt,
)
from features.study_units_generation.prompts.tests_prompt import (
    get_test_system_prompt,
)


def test_flashcards_prompt_defaults_to_basic_cards() -> None:
    prompt = get_flashcards_system_prompt()

    assert "basic_flashcards" in prompt


def test_flashcards_prompt_includes_every_requested_type() -> None:
    prompt = get_flashcards_system_prompt(
        flashcard_types=("basic", "cloze", "list")
    )

    assert "cloze_flashcards" in prompt
    assert "list_flashcards" in prompt


def test_flashcards_prompt_ignores_an_unknown_type() -> None:
    prompt = get_flashcards_system_prompt(flashcard_types=("mystery",))

    assert "deck_name" in prompt


def test_flashcards_prompt_states_the_amount_when_given() -> None:
    prompt = get_flashcards_system_prompt(amount=12)

    assert "Flashcards number: 12" in prompt


def test_flashcards_prompt_omits_the_amount_when_absent() -> None:
    prompt = get_flashcards_system_prompt(amount=None)

    assert "Flashcards number" not in prompt


def test_flashcards_prompt_carries_the_requested_settings() -> None:
    prompt = get_flashcards_system_prompt(
        comprehensiveness="high", verbosity="high"
    )

    assert "Comprehensiveness: high" in prompt
    assert "Flashcard verbosity: high" in prompt


def test_notes_prompt_asks_for_the_note_fields() -> None:
    prompt = get_notes_system_prompt()

    assert "note_content" in prompt
    assert "note_name" in prompt


def test_test_prompt_asks_for_multiple_choice_items() -> None:
    prompt = get_test_system_prompt()

    assert "multiple_choice_test_items" in prompt
    assert "test_name" in prompt


def test_the_output_format_is_a_json_object() -> None:
    prompt = get_flashcards_system_prompt()
    opening = prompt.index("```") + 3
    body = prompt[opening:].split("```")[0].strip()

    assert body.startswith("{")
    assert body.endswith("}")


def test_the_default_comprehensiveness_is_medium() -> None:
    assert "Comprehensiveness: medium" in get_flashcards_system_prompt()


def test_the_default_verbosity_is_low() -> None:
    assert "Flashcard verbosity: low" in get_flashcards_system_prompt()


def test_an_unknown_type_adds_nothing_to_the_format() -> None:
    known = get_flashcards_system_prompt(flashcard_types=("basic",))
    with_unknown = get_flashcards_system_prompt(
        flashcard_types=("basic", "mystery")
    )

    assert known == with_unknown


def test_only_the_requested_type_is_described() -> None:
    prompt = get_flashcards_system_prompt(flashcard_types=("cloze",))

    assert "cloze_flashcards" in prompt
    assert "basic_flashcards" not in prompt


def test_no_amount_leaves_the_constraint_line_empty() -> None:
    prompt = get_flashcards_system_prompt(amount=None)
    constraints = prompt.split("###Constraints###")[1]
    block = constraints.split("###Output format###")[0]
    lines = [line.strip() for line in block.splitlines() if line.strip()]

    assert lines == [
        "- Comprehensiveness: medium;",
        "- Flashcard verbosity: low;",
    ]
