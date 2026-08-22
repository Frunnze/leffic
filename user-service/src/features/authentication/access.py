from datetime import UTC, datetime, timedelta

import jwt

from shared.jwt_secret import SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def create_refresh_token(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)
