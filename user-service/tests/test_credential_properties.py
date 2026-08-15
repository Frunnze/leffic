from datetime import UTC, datetime
from typing import cast

import jwt
from hypothesis import given, settings
from hypothesis import strategies as st

from features.authentication.access import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
)
from shared.password_hashing import hash_password, verify_password

_BCRYPT_SAFE_TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=40,
)
_CLAIMS = st.dictionaries(
    st.sampled_from(["user_id", "email", "role"]),
    st.text(min_size=1, max_size=12),
    min_size=1,
)


def _expiry_of(token: str) -> float:
    payload: dict[str, object] = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM]
    )

    return cast("float", payload["exp"])


@settings(max_examples=10, deadline=None)
@given(_BCRYPT_SAFE_TEXT)
def test_hash_password_property_never_stores_the_password_itself(
    password: str,
) -> None:
    hashed = hash_password(password)

    assert hashed != password
    assert hashed != hash_password(password)


@settings(max_examples=10, deadline=None)
@given(_BCRYPT_SAFE_TEXT, _BCRYPT_SAFE_TEXT)
def test_verify_password_property_accepts_only_the_original_password(
    password: str, other_password: str
) -> None:
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password(other_password, hashed) is (
        other_password == password
    )


@settings(max_examples=50)
@given(_CLAIMS)
def test_create_access_token_property_carries_its_claims_and_an_expiry(
    claims: dict[str, str],
) -> None:
    payload = jwt.decode(
        create_access_token(claims), SECRET_KEY, algorithms=[ALGORITHM]
    )

    assert {key: payload[key] for key in claims} == claims
    assert payload["exp"] > datetime.now(UTC).timestamp()


@settings(max_examples=50)
@given(_CLAIMS)
def test_create_refresh_token_property_outlives_the_access_token(
    claims: dict[str, str],
) -> None:
    access_expiry = _expiry_of(create_access_token(claims))
    refresh_expiry = _expiry_of(create_refresh_token(claims))

    assert refresh_expiry > access_expiry
