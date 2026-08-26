from typing import Final

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    AmbiguousTokenSegmentError,
    signed_task_id,
    verified_task_id,
)
from tests.task_token_support import DIGEST_LENGTH, NOT_FOUND

_DOTLESS_TEXT: Final[st.SearchStrategy[str]] = st.text(
    alphabet=st.characters(blacklist_characters="."), max_size=24
)
_DOTTED_TEXT: Final[st.SearchStrategy[str]] = st.tuples(
    _DOTLESS_TEXT, _DOTLESS_TEXT
).map(".".join)
_IDENTIFIERS: Final[st.SearchStrategy[str]] = st.text(
    alphabet="abcdef0123456789-", min_size=1, max_size=40
)
_HEX_IDENTIFIERS: Final[st.SearchStrategy[str]] = st.text(
    alphabet="abcdef0123456789", min_size=1, max_size=40
)
_TOKEN_PART_COUNT: Final[int] = 3
_EXAMPLE_BUDGET: Final[int] = 50


def _refusal_of(token: str) -> HTTPException:
    with pytest.raises(HTTPException) as refusal:
        _ = verified_task_id(token)

    return refusal.value


def _mutated(token: str, position: int, replacement: str) -> str:
    index = position % len(token)

    return token[:index] + replacement + token[index + 1 :]


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_DOTLESS_TEXT, _DOTLESS_TEXT)
def test_verified_task_id_property_round_trips_signed_task_id(
    task_id: str, folder_id: str
) -> None:
    minted = signed_task_id(task_id, folder_id)

    assert verified_task_id(minted) == (task_id, folder_id)


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_DOTLESS_TEXT, _DOTLESS_TEXT)
def test_signed_task_id_property_is_deterministic_and_verifiable(
    task_id: str, folder_id: str
) -> None:
    minted = signed_task_id(task_id, folder_id)

    assert minted == signed_task_id(task_id, folder_id)
    assert verified_task_id(minted) == (task_id, folder_id)


@settings(max_examples=_EXAMPLE_BUDGET)
@given(
    _IDENTIFIERS,
    _IDENTIFIERS,
    st.integers(min_value=0),
    st.sampled_from("ghijkxyzGHIJK_+"),
)
def test_verified_task_id_property_rejects_any_mutated_character(
    task_id: str, folder_id: str, position: int, replacement: str
) -> None:
    minted = signed_task_id(task_id, folder_id)
    tampered = _mutated(minted, position, replacement)
    refusal = _refusal_of(tampered)

    assert tampered != minted
    assert refusal.status_code == NOT_FOUND
    assert refusal.detail == MISSING_TASK


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_IDENTIFIERS, _IDENTIFIERS)
def test_signed_task_id_property_keeps_its_three_part_shape(
    task_id: str, folder_id: str
) -> None:
    parts = signed_task_id(task_id, folder_id).split(".")

    assert len(parts) == _TOKEN_PART_COUNT
    assert parts[0] == task_id
    assert parts[1] == folder_id
    assert len(parts[2]) == DIGEST_LENGTH


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_IDENTIFIERS, _IDENTIFIERS, _IDENTIFIERS)
def test_signed_task_id_property_binds_the_token_to_one_folder(
    task_id: str, folder_id: str, other_folder_id: str
) -> None:
    digest = signed_task_id(task_id, folder_id).split(".")[2]
    rebound = f"{task_id}.{other_folder_id}.{digest}"

    if other_folder_id == folder_id:
        assert verified_task_id(rebound) == (task_id, folder_id)
    else:
        assert _refusal_of(rebound).detail == MISSING_TASK


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_IDENTIFIERS, _IDENTIFIERS, _IDENTIFIERS)
def test_signed_task_id_property_binds_the_token_to_one_task(
    task_id: str, folder_id: str, other_task_id: str
) -> None:
    digest = signed_task_id(task_id, folder_id).split(".")[2]
    rebound = f"{other_task_id}.{folder_id}.{digest}"

    if other_task_id == task_id:
        assert verified_task_id(rebound) == (task_id, folder_id)
    else:
        assert _refusal_of(rebound).detail == MISSING_TASK


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_HEX_IDENTIFIERS, _HEX_IDENTIFIERS, _HEX_IDENTIFIERS)
def test_signed_task_id_property_separates_neighbouring_inputs(
    first_part: str, second_part: str, third_part: str
) -> None:
    left = signed_task_id(first_part, second_part + third_part)
    right = signed_task_id(first_part + second_part, third_part)

    assert left.split(".")[2] != right.split(".")[2]


@settings(max_examples=_EXAMPLE_BUDGET)
@given(st.lists(_IDENTIFIERS, min_size=1, max_size=6, unique=True))
def test_signed_task_id_property_never_reuses_a_digest(
    folder_ids: list[str],
) -> None:
    digests = {
        signed_task_id("shared-task", folder_id).split(".")[2]
        for folder_id in folder_ids
    }

    assert len(digests) == len(folder_ids)


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_IDENTIFIERS, _IDENTIFIERS)
def test_verified_task_id_property_is_free_of_side_effects(
    task_id: str, folder_id: str
) -> None:
    minted = signed_task_id(task_id, folder_id)

    assert verified_task_id(minted) == verified_task_id(minted)


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_IDENTIFIERS, _IDENTIFIERS)
def test_verified_task_id_property_refuses_a_truncated_digest(
    task_id: str, folder_id: str
) -> None:
    minted = signed_task_id(task_id, folder_id)

    assert _refusal_of(minted[:-1]).status_code == NOT_FOUND
    assert _refusal_of(minted[:-1]).detail == MISSING_TASK


@settings(max_examples=_EXAMPLE_BUDGET)
@given(_DOTTED_TEXT, _DOTLESS_TEXT)
def test_signed_task_id_property_refuses_a_segment_separator(
    dotted: str, plain: str
) -> None:
    with pytest.raises(AmbiguousTokenSegmentError):
        _ = signed_task_id(dotted, plain)

    with pytest.raises(AmbiguousTokenSegmentError):
        _ = signed_task_id(plain, dotted)
