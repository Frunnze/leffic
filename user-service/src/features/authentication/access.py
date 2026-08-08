import os
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

_configured_key = os.getenv("JWT_SECRET_KEY")
if not _configured_key:
    _UNSET_ENVIRONMENT = "JWT_SECRET_KEY environment variable is not set"
    raise RuntimeError(_UNSET_ENVIRONMENT)
SECRET_KEY: str = _configured_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def create_access_token(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
