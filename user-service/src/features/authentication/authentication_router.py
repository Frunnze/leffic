from typing import Annotated

import jwt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse

from features.authentication import cookie_security
from features.authentication.access import (
    create_access_token,
    create_refresh_token,
)
from features.authentication.database_user_registry import (
    DatabaseUserRegistry,
)
from features.authentication.schemas import UserCreate, UserLogin
from features.authentication.user_registry import UserRegistry
from shared.jwt_secret import ALGORITHM, SECRET_KEY
from shared.models import User
from shared.password_hashing import hash_password, verify_password

auth = APIRouter()

RegisteredUsers = Annotated[UserRegistry, Depends(DatabaseUserRegistry)]

_ISSUER = "my-issuer"
_REFRESH_COOKIE = "refresh_token"
_INVALID_CREDENTIALS = "Invalid token"
_USERNAME_REGISTERED = "username_registered"
_EMAIL_REGISTERED = "email_registered"
_UNKNOWN_EMAIL = "Incorrect email"
_WRONG_CREDENTIALS = "Incorrect password"


def _issue_refresh_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,
        samesite="strict",
        secure=cookie_security.REFRESH_COOKIE_SECURE,
    )


def _session_payload(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
    }


@auth.post("/sign-up", response_model=None)
def register_user(
    user: UserCreate, response: Response, users: RegisteredUsers
) -> JSONResponse | dict[str, str]:
    if users.user_named(user.username) is not None:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"code": _USERNAME_REGISTERED},
        )

    if users.user_with_email(user.email) is not None:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"code": _EMAIL_REGISTERED},
        )

    registered_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    users.register(registered_user)

    user_id = str(registered_user.id)

    _issue_refresh_cookie(response, user_id)

    return _session_payload(
        registered_user,
        create_access_token(data={"user_id": user_id, "iss": _ISSUER}),
    )


@auth.post("/login", response_model=None)
def login_user(
    user_login: UserLogin, response: Response, users: RegisteredUsers
) -> JSONResponse | dict[str, str]:
    user = users.user_with_email(user_login.email)

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": _UNKNOWN_EMAIL},
        )

    if not verify_password(user_login.password, user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": _WRONG_CREDENTIALS},
        )

    user_id = str(user.id)

    _issue_refresh_cookie(response, user_id)

    return _session_payload(
        user,
        create_access_token(data={"user_id": user_id, "iss": _ISSUER}),
    )


@auth.post("/refresh-token")
def refresh_token(request: Request) -> dict[str, str]:
    token = request.cookies.get(_REFRESH_COOKIE)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    user_id = _refreshed_user_id(token)

    return {
        "access_token": create_access_token(
            {"user_id": user_id, "iss": _ISSUER}
        ),
        "user_id": user_id,
    }


def _refreshed_user_id(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


@auth.post("/logout")
def logout_user(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=_REFRESH_COOKIE,
        httponly=True,
        samesite="strict",
        secure=cookie_security.REFRESH_COOKIE_SECURE,
        path="/",
    )
    response.status_code = status.HTTP_200_OK

    return {"message": "Successfully logged out"}
