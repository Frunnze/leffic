import os
from datetime import UTC, datetime, timedelta

import jwt

_configured_key = os.getenv("JWT_SECRET_KEY")
if not _configured_key:
    _UNSET_ENVIRONMENT = "JWT_SECRET_KEY environment variable is not set"
    raise RuntimeError(_UNSET_ENVIRONMENT)
SECRET_KEY: str = _configured_key
ALGORITHM = "HS256"
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
