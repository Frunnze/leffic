from typing import Final

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    _encoded,
    _refusal,
    _signature_of,
)
from tests.task_token_support import DIGEST_LENGTH, NOT_FOUND

_SURROGATE_CHARACTERS: Final[st.SearchStrategy[str]] = st.characters(
    categories=("Cs",)
)
_ANY_CHARACTER: Final[st.SearchStrategy[str]] = st.one_of(
    st.characters(), _SURROGATE_CHARACTERS
)
_ANY_TEXT: Final[st.SearchStrategy[str]] = st.text(
    alphabet=_ANY_CHARACTER, max_size=24
)
_HEXADECIMAL_DIGITS: Final[str] = "0123456789abcdef"
_EXAMPLE_BUDGET: Final[int] = 50
_TEXT_ENCODING: Final[str] = "utf-8"
_SURROGATE_HANDLING: Final[str] = "surrogatepass"
_REFUSAL_COUNT_CEILING: Final[int] = 5


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_ANY_TEXT)
def test__encoded_property_round_trips_every_string(text: str) -> None:
    encoded = _encoded(text)

    assert isinstance(encoded, bytes)
    assert encoded.decode(_TEXT_ENCODING, _SURROGATE_HANDLING) == text


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_ANY_TEXT, _ANY_TEXT)
def test__signature_of_property_is_a_stable_lowercase_hex_digest(
    task_id: str, folder_id: str
) -> None:
    signature = _signature_of(task_id, folder_id)

    assert signature == _signature_of(task_id, folder_id)
    assert len(signature) == DIGEST_LENGTH
    assert set(signature) <= set(_HEXADECIMAL_DIGITS)


@settings(max_examples=_EXAMPLE_BUDGET)
@given(st.integers(min_value=1, max_value=_REFUSAL_COUNT_CEILING))
def test__refusal_property_always_reports_the_same_missing_task_404(
    requested_count: int,
) -> None:
    refusals = [_refusal() for _ in range(requested_count)]

    assert len(refusals) == requested_count
    assert {refusal.status_code for refusal in refusals} == {NOT_FOUND}
    assert {refusal.detail for refusal in refusals} == {MISSING_TASK}
