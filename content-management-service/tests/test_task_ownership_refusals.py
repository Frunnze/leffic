from typing import Final

import pytest
from fastapi import HTTPException

from features.study_units_generation import task_ownership
from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    AmbiguousTokenSegmentError,
    signed_task_id,
    verified_task_id,
)
from tests.task_token_support import NOT_FOUND

_TASK_ID: Final[str] = "9d0f1a2b-0000-4000-8000-00000000c001"
_FOLDER_ID: Final[str] = "9d0f1a2b-0000-4000-8000-00000000d002"
_OTHER_FOLDER_ID: Final[str] = "9d0f1a2b-0000-4000-8000-00000000d003"
_FOREIGN_SIGNING_KEY: Final[str] = "a-different-secret-than-the-real-one"
_DOTTED_SEGMENTS: Final[tuple[tuple[str, str], ...]] = (
    ("a", "b.c"),
    ("a.b", "c"),
    ("a.b", "c.d"),
    (".", ""),
)


def test_a_swapped_folder_segment_is_refused() -> None:
    digest = signed_task_id(_TASK_ID, _FOLDER_ID).split(".")[2]
    swapped = f"{_TASK_ID}.{_OTHER_FOLDER_ID}.{digest}"

    with pytest.raises(HTTPException) as refusal:
        _ = verified_task_id(swapped)

    assert refusal.value.status_code == NOT_FOUND
    assert refusal.value.detail == MISSING_TASK


def test_a_token_signed_with_another_secret_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        task_ownership, "SECRET_KEY", _FOREIGN_SIGNING_KEY, raising=True
    )
    foreign = signed_task_id(_TASK_ID, _FOLDER_ID)
    monkeypatch.undo()

    with pytest.raises(HTTPException) as refusal:
        _ = verified_task_id(foreign)

    assert refusal.value.detail == MISSING_TASK


def test_a_different_folder_produces_a_different_digest() -> None:
    first = signed_task_id(_TASK_ID, _FOLDER_ID).split(".")[2]
    second = signed_task_id(_TASK_ID, _OTHER_FOLDER_ID).split(".")[2]

    assert first != second


@pytest.mark.parametrize(("task_id", "folder_id"), _DOTTED_SEGMENTS)
def test_a_segment_carrying_the_separator_is_refused(
    task_id: str, folder_id: str
) -> None:
    with pytest.raises(AmbiguousTokenSegmentError):
        _ = signed_task_id(task_id, folder_id)


def test_the_two_readings_of_one_token_can_no_longer_be_minted() -> None:
    with pytest.raises(AmbiguousTokenSegmentError):
        _ = signed_task_id("a", "b.c")

    with pytest.raises(AmbiguousTokenSegmentError):
        _ = signed_task_id("a.b", "c")
