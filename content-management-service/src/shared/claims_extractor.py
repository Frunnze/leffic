from typing import Annotated

import jwt
from fastapi import Header, HTTPException, status

_BEARER_SCHEME = "bearer"
_BEARER_HEADER_PARTS = 2
_MISSING_USER_ID = "Token carries no user_id"


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

    return user_id


def _decode_claims(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def _bearer_token(authorization: str | None) -> str:
    parts = (authorization or "").split()

    if (
        len(parts) != _BEARER_HEADER_PARTS
        or parts[0].lower() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: expected a bearer scheme",
        )

    return parts[1]
