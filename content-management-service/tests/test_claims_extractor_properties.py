import uuid

import jwt
import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.claims_extractor import (
    _bearer_token,
    _decode_claims,
    _validated_user_id,
    get_user_id_from_jwt,
)

_UNAUTHORIZED = 401
_SIGNING_KEY = "a" * 32
_BEARER_PARTS = 2
_SCHEMES = st.sampled_from(["Bearer", "bearer", "BEARER", "BeArEr"])
_TOKEN_TEXT = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=1,
    max_size=20,
)
_ANOTHER_SCHEME = _TOKEN_TEXT.filter(
    lambda word: word.lower() != "bearer"
)


def _bearer_header(user_id: str) -> str:
    return f"Bearer {jwt.encode({'user_id': user_id}, _SIGNING_KEY)}"


@settings(max_examples=50)
@given(_SCHEMES, _TOKEN_TEXT)
def test__bearer_token_property_accepts_the_scheme_in_any_case(
    scheme: str, token: str
) -> None:
    assert _bearer_token(f"{scheme} {token}") == token


@settings(max_examples=50)
@given(
    st.lists(_TOKEN_TEXT, max_size=4).filter(
        lambda parts: len(parts) != _BEARER_PARTS
    )
)
def test__bearer_token_property_rejects_anything_but_two_parts(
    parts: list[str],
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = _bearer_token(" ".join(parts))

    assert raised.value.status_code == _UNAUTHORIZED


@settings(max_examples=50)
@given(_ANOTHER_SCHEME, _TOKEN_TEXT)
def test__bearer_token_property_rejects_another_scheme(
    scheme: str, token: str
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = _bearer_token(f"{scheme} {token}")

    assert raised.value.status_code == _UNAUTHORIZED


@settings(max_examples=50)
@given(st.dictionaries(_TOKEN_TEXT, _TOKEN_TEXT, max_size=4))
def test__decode_claims_property_returns_every_claim_it_was_given(
    claims: dict[str, str],
) -> None:
    token = jwt.encode(claims, _SIGNING_KEY)

    assert _decode_claims(f"Bearer {token}") == claims


@settings(max_examples=50)
@given(st.uuids())
def test__validated_user_id_property_passes_a_uuid_through_unchanged(
    identifier: uuid.UUID,
) -> None:
    assert _validated_user_id(str(identifier)) == str(identifier)


@settings(max_examples=50)
@given(st.text(max_size=12))
def test__validated_user_id_property_rejects_what_is_not_a_uuid(
    identifier: str,
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = _validated_user_id(identifier)

    assert raised.value.status_code == _UNAUTHORIZED


@settings(max_examples=50)
@given(st.uuids())
def test_get_user_id_from_jwt_property_returns_the_carried_user_id(
    identifier: uuid.UUID,
) -> None:
    assert get_user_id_from_jwt(_bearer_header(str(identifier))) == str(
        identifier
    )
