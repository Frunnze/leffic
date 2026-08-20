import uuid

import pytest
from fastapi import HTTPException

from shared.identifiers import parsed_identifier
from tests.access_support import MISSING_DECK, MISSING_UNIT

_NOT_FOUND = 404

_CANONICAL = "6f1c7d4e-0000-4000-8000-0000000000aa"
_HYPHENLESS = "6f1c7d4e000040008000000000000aa0"
_REJECTED_VALUES = (
    "",
    " ",
    "\t\n",
    "not-a-uuid",
    "6f1c7d4e-0000-4000-8000",
    "6f1c7d4e-0000-4000-8000-0000000000a",
    "' OR 1=1 --",
    "home",
    "None",
    "null",
    "../../etc/passwd",
    "ünïcødé",
    "x" * 5000,
)


def test_a_canonical_uuid_is_parsed_unchanged() -> None:
    assert parsed_identifier(_CANONICAL, MISSING_UNIT) == uuid.UUID(_CANONICAL)


def test_an_uppercase_uuid_parses_to_the_same_value() -> None:
    assert parsed_identifier(_CANONICAL.upper(), MISSING_UNIT) == uuid.UUID(
        _CANONICAL
    )


def test_a_hyphenless_uuid_is_parsed() -> None:
    assert parsed_identifier(_HYPHENLESS, MISSING_UNIT) == uuid.UUID(
        _HYPHENLESS
    )


def test_a_malformed_value_is_refused_as_a_missing_unit() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier("not-a-uuid", MISSING_UNIT)

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == MISSING_UNIT


def test_an_empty_value_is_refused_as_a_missing_unit() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier("", MISSING_UNIT)

    assert raised.value.status_code == _NOT_FOUND


def test_a_truncated_uuid_is_refused_as_a_missing_unit() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier("6f1c7d4e-0000-4000-8000", MISSING_UNIT)

    assert raised.value.status_code == _NOT_FOUND


def test_a_sql_payload_is_refused_as_a_missing_unit() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier("' OR 1=1 --", MISSING_UNIT)

    assert raised.value.status_code == _NOT_FOUND


def test_the_home_alias_is_not_an_identifier() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier("home", MISSING_UNIT)

    assert raised.value.status_code == _NOT_FOUND


def test_the_detail_the_caller_passes_is_the_detail_reported() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier("not-a-uuid", MISSING_DECK)

    assert raised.value.detail == MISSING_DECK


@pytest.mark.parametrize("value", _REJECTED_VALUES)
def test_no_hostile_value_ever_parses(value: str) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier(value, MISSING_UNIT)

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == MISSING_UNIT
