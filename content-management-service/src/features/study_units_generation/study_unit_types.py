from typing import NamedTuple


class StudyUnitType(NamedTuple):
    name: str
    prompt_file: str
    result_key: str


_FLASHCARD_TYPES = (
    StudyUnitType("basic", "flashcards/basic", "basic_flashcards"),
    StudyUnitType("cloze", "flashcards/cloze", "cloze_flashcards"),
    StudyUnitType("feynman", "flashcards/feynman", "feynman_flashcards"),
    StudyUnitType("list", "flashcards/list", "list_flashcards"),
)

_TEST_ITEM_TYPES = (
    StudyUnitType(
        "multiple_choice",
        "test_items/multiple_choice",
        "multiple_choice_test_items",
    ),
    StudyUnitType(
        "true_or_false",
        "test_items/true_or_false",
        "true_or_false_test_items",
    ),
    StudyUnitType(
        "short_answer",
        "test_items/short_answer",
        "short_answer_test_items",
    ),
)

DEFAULT_FLASHCARD_TYPES = ("basic",)
DEFAULT_TEST_ITEM_TYPES = ("multiple_choice",)
NOTE_PROMPT_FILE = "note"

_BY_NAME = {
    unit_type.name: unit_type
    for unit_type in _FLASHCARD_TYPES + _TEST_ITEM_TYPES
}

_UNKNOWN_TYPE = "No study unit type named"


class UnknownStudyUnitTypeError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"{_UNKNOWN_TYPE} {name}")


def study_unit_type(name: str) -> StudyUnitType:
    unit_type = _BY_NAME.get(name)

    if unit_type is None:
        raise UnknownStudyUnitTypeError(name)

    return unit_type


def requested_names(
    requested: tuple[str, ...], fallback: tuple[str, ...]
) -> tuple[str, ...]:
    known = tuple(name for name in requested if name in _BY_NAME)

    return known or fallback
