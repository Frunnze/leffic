from features.study_units_generation.study_unit_types import (
    NOTE_PROMPT_FILE,
    study_unit_type,
)

FLASHCARD_TYPES = ("basic", "cloze", "feynman", "list")
ITEM_TYPES = ("multiple_choice", "true_or_false", "short_answer")
GENERATED_TYPES = FLASHCARD_TYPES + ITEM_TYPES


def every_prompt_file() -> tuple[str, ...]:
    generated = tuple(
        study_unit_type(name).prompt_file for name in GENERATED_TYPES
    )

    return (NOTE_PROMPT_FILE, *generated)
