import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.study_unit_types import (
    DEFAULT_FLASHCARD_TYPES,
    UnknownStudyUnitTypeError,
    requested_names,
    study_unit_type,
)

_KNOWN = (
    "basic",
    "cloze",
    "feynman",
    "list",
    "multiple_choice",
    "true_or_false",
    "short_answer",
)
_NAMES = st.sampled_from(_KNOWN)


@settings(max_examples=50)
@given(_NAMES)
def test_study_unit_type_property_answers_with_the_type_it_was_asked_for(
    name: str,
) -> None:
    unit_type = study_unit_type(name)

    assert unit_type.name == name
    assert unit_type.result_key.startswith(name)
    assert unit_type.prompt_file.endswith(name)


@settings(max_examples=50)
@given(st.text(max_size=12))
def test_study_unit_type_property_refuses_a_type_it_does_not_know(
    name: str,
) -> None:
    if name in _KNOWN:
        return

    with pytest.raises(UnknownStudyUnitTypeError) as refused:
        _ = study_unit_type(name)

    assert str(refused.value) == f"No study unit type named {name}"


@settings(max_examples=50)
@given(st.lists(st.text(max_size=8), max_size=5))
def test_requested_names_property_keeps_only_the_types_it_knows(
    requested: list[str],
) -> None:
    kept = requested_names(tuple(requested), DEFAULT_FLASHCARD_TYPES)

    assert all(name in _KNOWN for name in kept)
    assert kept


@settings(max_examples=50)
@given(st.lists(_NAMES, min_size=1, max_size=4, unique=True))
def test_requested_names_property_preserves_what_was_asked_for(
    requested: list[str],
) -> None:
    assert requested_names(
        tuple(requested), DEFAULT_FLASHCARD_TYPES
    ) == tuple(requested)
