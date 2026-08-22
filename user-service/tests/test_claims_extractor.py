import jwt
import pytest
from fastapi import HTTPException

from features.account.claims_extractor import get_user_id_from_jwt
from shared.jwt_secret import ALGORITHM, SECRET_KEY

_UNAUTHORIZED = 401

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"


def _bearer(claims: dict[str, object]) -> str:
    return f"Bearer {jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)}"


def test_returns_user_id_from_bearer_token() -> None:
    header = _bearer({"user_id": _USER_ID})

    assert get_user_id_from_jwt(header) == _USER_ID


def test_accepts_lowercase_scheme() -> None:
    header = _bearer({"user_id": _USER_ID}).replace("Bearer", "bearer")

    assert get_user_id_from_jwt(header) == _USER_ID


def test_rejects_missing_header() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(None)

    assert raised.value.status_code == _UNAUTHORIZED
    assert raised.value.detail == "Invalid token: expected a bearer scheme"


def test_rejects_header_without_scheme() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt("just-a-token")

    assert raised.value.status_code == _UNAUTHORIZED
    assert raised.value.detail == "Invalid token: expected a bearer scheme"


def test_rejects_wrong_scheme() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt("Basic abcdef")

    assert raised.value.status_code == _UNAUTHORIZED
    assert raised.value.detail == "Invalid token: expected a bearer scheme"


def test_rejects_malformed_token() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt("Bearer not-a-jwt")

    assert raised.value.status_code == _UNAUTHORIZED
    assert str(raised.value.detail).startswith("Invalid token: ")


def test_rejects_a_token_signed_with_the_wrong_key() -> None:
    forged = jwt.encode(
        {"user_id": _USER_ID}, "a-forged-key", algorithm=ALGORITHM
    )

    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(f"Bearer {forged}")

    assert raised.value.status_code == _UNAUTHORIZED
    assert str(raised.value.detail).startswith("Invalid token: ")


def test_rejects_token_without_user_id() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(_bearer({"sub": "nobody"}))

    assert raised.value.status_code == _UNAUTHORIZED
    assert raised.value.detail == "Token carries no user_id"


def test_rejects_non_string_user_id() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(_bearer({"user_id": 12345}))

    assert raised.value.status_code == _UNAUTHORIZED
    assert raised.value.detail == "Token carries no user_id"


@pytest.mark.parametrize(
    "claim", ["hello", "", "home", "6f1c7d4e-0000-4000-8000", "' OR 1=1 --"]
)
def test_rejects_user_id_that_is_not_a_uuid(claim: str) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(_bearer({"user_id": claim}))

    assert raised.value.status_code == _UNAUTHORIZED
    assert raised.value.detail == "Token carries an invalid user_id"


def test_accepts_an_uppercase_user_id() -> None:
    header = _bearer({"user_id": _USER_ID.upper()})

    assert get_user_id_from_jwt(header) == _USER_ID.upper()
