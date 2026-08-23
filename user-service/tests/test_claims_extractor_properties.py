import uuid

import jwt
import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.account.claims_extractor import (
    _bearer_token,
    _decode_claims,
    _validated_user_id,
    get_user_id_from_jwt,
)
from shared.jwt_secret import SECRET_KEY

_UNAUTHORIZED = 401
_SCHEMES = st.sampled_from(["Bearer", "bearer", "BEARER", "BeArEr"])
_TOKEN_TEXT = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=1,
    max_size=20,
)


def _bearer_header(user_id: str) -> str:
    return f"Bearer {jwt.encode({'user_id': user_id}, SECRET_KEY)}"


@settings(max_examples=50)
@given(_SCHEMES, _TOKEN_TEXT)
def test__bearer_token_property_accepts_the_scheme_in_any_case(
    scheme: str, token: str
) -> None:
    assert _bearer_token(f"{scheme} {token}") == token


@settings(max_examples=50)
@given(
    st.one_of(
        st.lists(_TOKEN_TEXT, min_size=0, max_size=1),
        st.lists(_TOKEN_TEXT, min_size=3, max_size=4),
    )
)
def test__bearer_token_property_rejects_anything_but_two_parts(
    parts: list[str],
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = _bearer_token(" ".join(parts))

    assert raised.value.status_code == _UNAUTHORIZED


@settings(max_examples=50)
@given(st.dictionaries(_TOKEN_TEXT, _TOKEN_TEXT, max_size=4))
def test__decode_claims_property_returns_every_claim_it_was_given(
    claims: dict[str, str],
) -> None:
    token = jwt.encode(claims, SECRET_KEY)

    assert _decode_claims(f"Bearer {token}") == claims


@settings(max_examples=50)
@given(st.uuids())
def test__validated_user_id_property_passes_a_uuid_through_unchanged(
    identifier: uuid.UUID,
) -> None:
    assert _validated_user_id(str(identifier)) == str(identifier)


@settings(max_examples=50)
@given(st.uuids())
def test_get_user_id_from_jwt_property_returns_the_carried_user_id(
    identifier: uuid.UUID,
) -> None:
    header = _bearer_header(str(identifier))

    assert get_user_id_from_jwt(header) == str(identifier)
