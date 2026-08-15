from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.prompts.flashcards_prompt import (
    _output_format,
    get_flashcards_system_prompt,
)
from features.study_units_generation.prompts.notes_prompt import (
    get_notes_system_prompt,
)
from features.study_units_generation.prompts.tests_prompt import (
    get_test_system_prompt,
)

_CARD_TYPES = ("basic", "cloze", "feynman", "list")
_ITEM_TYPES = ("multiple_choice", "true_or_false", "short_answer")
_UNKNOWN = st.sampled_from(["unheard-of", "", "BASIC", "cloze_flashcards"])
_LEVELS = st.sampled_from(["high", "medium", "low"])


@settings(max_examples=50)
@given(st.lists(st.sampled_from(_CARD_TYPES), unique=True, min_size=1))
def test__output_format_property_names_every_type_that_was_asked_for(
    requested: list[str],
) -> None:
    written = _output_format(tuple(requested))

    assert all(f'"{name}_flashcards"' in written for name in requested)
    assert '"deck_name"' in written


@settings(max_examples=50)
@given(st.lists(_UNKNOWN, max_size=3))
def test__output_format_property_falls_back_when_no_type_is_known(
    unknown: list[str],
) -> None:
    assert _output_format(tuple(unknown)) == _output_format(("basic",))


@settings(max_examples=50)
@given(_LEVELS, _LEVELS, st.one_of(st.none(), st.integers(0, 200)))
def test_get_flashcards_system_prompt_property_states_its_constraints(
    comprehensiveness: str, verbosity: str, amount: int | None
) -> None:
    written = get_flashcards_system_prompt(
        comprehensiveness=comprehensiveness,
        verbosity=verbosity,
        amount=amount,
    )

    assert f"Comprehensiveness: {comprehensiveness};" in written
    assert f"Flashcard verbosity: {verbosity};" in written
    assert ("Flashcards number:" in written) is bool(amount)


@settings(max_examples=50)
@given(st.lists(st.sampled_from(_ITEM_TYPES), unique=True, min_size=1))
def test_get_test_system_prompt_property_names_every_item_type_asked_for(
    requested: list[str],
) -> None:
    written = get_test_system_prompt(tuple(requested))

    assert all(f'"{name}_test_items"' in written for name in requested)
    assert '"test_name"' in written


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=3))
def test_get_notes_system_prompt_property_always_asks_for_the_same_shape(
    count: int,
) -> None:
    written = [get_notes_system_prompt() for _ in range(count)]

    assert len(set(written)) == 1
    assert '"note_content"' in written[0]
    assert '"note_name"' in written[0]
