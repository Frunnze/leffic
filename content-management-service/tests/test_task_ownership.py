import ast
import hashlib
import hmac
import inspect
from collections.abc import Callable
from typing import Final

import pytest
from fastapi import HTTPException

from features.study_units_generation import task_ownership
from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    signed_task_id,
    verified_task_id,
)
from shared.jwt_secret import SECRET_KEY
from tests.task_token_support import DIGEST_LENGTH, NOT_FOUND

_FORBIDDEN_PREFIXES: Final[tuple[str, ...]] = (
    "celery",
    "sqlalchemy",
    "shared.models",
)
_MALFORMED_TOKENS: Final[tuple[str, ...]] = (
    "",
    "a",
    "a.b",
    "a.b.c.d",
    "a.b.zzz",
)
_TASK_ID: Final[str] = "9d0f1a2b-0000-4000-8000-00000000c001"
_FOLDER_ID: Final[str] = "9d0f1a2b-0000-4000-8000-00000000d002"
_TOKEN_PART_COUNT: Final[int] = 3


class _ComparisonSpy:
    def __init__(
        self, original: Callable[[str, str], bool]
    ) -> None:
        self.original: Callable[[str, str], bool] = original
        self.call_count: int = 0

    def __call__(self, left: str, right: str) -> bool:
        self.call_count += 1

        return self.original(left, right)


def _imported_module_names() -> set[str]:
    parsed = ast.parse(inspect.getsource(task_ownership))
    names: set[str] = set()

    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)

        if isinstance(node, ast.ImportFrom):
            names.add(node.module or "")

    return names


def _exclamation_literals() -> set[str]:
    parsed = ast.parse(inspect.getsource(task_ownership))

    return {
        node.value
        for node in ast.walk(parsed)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.endswith("!")
    }


def _plain_hmac_digest(message: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(), message.encode(), hashlib.sha256
    ).hexdigest()


def test_module_uses_only_standard_library_crypto() -> None:
    assert {"hmac", "hashlib"} <= _imported_module_names()


def test_missing_task_detail_is_the_single_constant() -> None:
    assert MISSING_TASK == "Task does not exist!"
    assert _exclamation_literals() == {MISSING_TASK}


def test_signed_task_id_has_three_dot_separated_parts() -> None:
    parts = signed_task_id(_TASK_ID, _FOLDER_ID).split(".")

    assert len(parts) == _TOKEN_PART_COUNT
    assert parts[0] == _TASK_ID
    assert parts[1] == _FOLDER_ID
    assert len(parts[2]) == DIGEST_LENGTH
    assert parts[2] == parts[2].lower()


def test_signature_is_domain_separated_from_plain_hmac() -> None:
    digest = signed_task_id(_TASK_ID, _FOLDER_ID).split(".")[2]
    unprefixed = {
        _plain_hmac_digest(_TASK_ID + _FOLDER_ID),
        _plain_hmac_digest(f"{_TASK_ID}.{_FOLDER_ID}"),
        _plain_hmac_digest(f"{_TASK_ID}:{_FOLDER_ID}"),
    }

    assert digest not in unprefixed


def test_verified_task_id_uses_constant_time_comparison(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = _ComparisonSpy(hmac.compare_digest)
    monkeypatch.setattr(hmac, "compare_digest", spy)

    assert verified_task_id(signed_task_id(_TASK_ID, _FOLDER_ID)) == (
        _TASK_ID,
        _FOLDER_ID,
    )
    assert spy.call_count >= 1


@pytest.mark.parametrize("token", _MALFORMED_TOKENS)
def test_malformed_tokens_are_404(token: str) -> None:
    with pytest.raises(HTTPException) as refusal:
        _ = verified_task_id(token)

    assert refusal.value.status_code == NOT_FOUND
    assert refusal.value.detail == MISSING_TASK


def test_verification_touches_no_database_or_celery() -> None:
    imported = _imported_module_names()

    assert not [
        name
        for name in imported
        if name.startswith(_FORBIDDEN_PREFIXES)
    ]


def test_verified_task_id_returns_both_identifiers() -> None:
    minted = signed_task_id(_TASK_ID, _FOLDER_ID)

    assert verified_task_id(minted) == (_TASK_ID, _FOLDER_ID)


def test_signed_task_id_is_stable_for_the_same_inputs() -> None:
    first = signed_task_id(_TASK_ID, _FOLDER_ID)
    second = signed_task_id(_TASK_ID, _FOLDER_ID)

    assert first == second
