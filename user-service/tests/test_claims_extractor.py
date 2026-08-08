import jwt
import pytest
from fastapi import HTTPException

from src.shared.claims_extractor import get_user_id_from_jwt

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"


def _bearer(claims: dict[str, object]) -> str:
    return f"Bearer {jwt.encode(claims, 'secret', algorithm='HS256')}"


def test_returns_user_id_from_bearer_token() -> None:
    header = _bearer({"user_id": _USER_ID})

    assert get_user_id_from_jwt(header) == _USER_ID


def test_accepts_lowercase_scheme() -> None:
    header = _bearer({"user_id": _USER_ID}).replace("Bearer", "bearer")

    assert get_user_id_from_jwt(header) == _USER_ID


def test_rejects_missing_header() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(None)

    assert raised.value.status_code == 401


def test_rejects_header_without_scheme() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt("just-a-token")

    assert raised.value.status_code == 401


def test_rejects_wrong_scheme() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt("Basic abcdef")

    assert "bearer scheme" in str(raised.value.detail)


def test_rejects_malformed_token() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt("Bearer not-a-jwt")

    assert "Invalid token" in str(raised.value.detail)


def test_rejects_token_without_user_id() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(_bearer({"sub": "nobody"}))

    assert raised.value.detail == "Token carries no user_id"


def test_rejects_non_string_user_id() -> None:
    with pytest.raises(HTTPException) as raised:
        _ = get_user_id_from_jwt(_bearer({"user_id": 12345}))

    assert raised.value.detail == "Token carries no user_id"
