import uuid
from typing import Annotated

import jwt
from fastapi import Header, HTTPException, status

from shared.jwt_secret import ALGORITHM, SECRET_KEY

_BEARER_SCHEME = "bearer"
_BEARER_HEADER_PARTS = 2
_MISSING_USER_ID = "Token carries no user_id"
_INVALID_USER_ID = "Token carries an invalid user_id"
_MISSING_SCHEME = "Invalid token: expected a bearer scheme"


def get_user_id_from_jwt(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return _validated_user_id(user_id)


def _validated_user_id(user_id: str) -> str:
    try:
        _ = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_USER_ID,
        ) from None

    return user_id


def _decode_claims(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def _bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = authorization.split()

    if (
        len(parts) != _BEARER_HEADER_PARTS
        or parts[0].lower() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]
