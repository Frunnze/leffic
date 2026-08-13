from datetime import UTC, datetime, timedelta

import jwt

from features.authentication.access import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
)
from shared.password_hashing import hash_password, verify_password

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_LOGIN_PHRASE = "correct horse battery staple"
_CLOCK_TOLERANCE = 5


def _claims(token: str) -> dict[str, object]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_hashing_does_not_keep_the_plain_password() -> None:
    hashed = hash_password(_LOGIN_PHRASE)

    assert _LOGIN_PHRASE not in hashed


def test_verifying_the_right_password_succeeds() -> None:
    assert verify_password(_LOGIN_PHRASE, hash_password(_LOGIN_PHRASE))


def test_verifying_the_wrong_password_fails() -> None:
    assert not verify_password("wrong", hash_password(_LOGIN_PHRASE))


def test_the_same_password_hashes_differently_each_time() -> None:
    assert hash_password(_LOGIN_PHRASE) != hash_password(_LOGIN_PHRASE)


def test_access_token_carries_the_user_id() -> None:
    token = create_access_token({"user_id": _USER_ID})

    assert _claims(token)["user_id"] == _USER_ID


def test_access_token_expires_in_utc() -> None:
    token = create_access_token({"user_id": _USER_ID})
    expected = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expires_at = int(str(_claims(token)["exp"]))

    assert abs(expires_at - expected.timestamp()) < _CLOCK_TOLERANCE


def test_access_token_honours_a_custom_lifetime() -> None:
    short = create_access_token(
        {"user_id": _USER_ID}, expires_delta=timedelta(minutes=1)
    )
    default = create_access_token({"user_id": _USER_ID})

    assert int(str(_claims(short)["exp"])) < int(
        str(_claims(default)["exp"])
    )


def test_refresh_token_expires_in_utc() -> None:
    token = create_refresh_token({"user_id": _USER_ID})
    expected = datetime.now(UTC) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    expires_at = int(str(_claims(token)["exp"]))

    assert abs(expires_at - expected.timestamp()) < _CLOCK_TOLERANCE


def test_refresh_token_outlives_the_access_token() -> None:
    access = create_access_token({"user_id": _USER_ID})
    refresh = create_refresh_token({"user_id": _USER_ID})

    assert int(str(_claims(refresh)["exp"])) > int(
        str(_claims(access)["exp"])
    )


def test_tokens_are_signed_with_the_configured_algorithm() -> None:
    token = create_access_token({"user_id": _USER_ID})

    assert jwt.get_unverified_header(token)["alg"] == ALGORITHM
