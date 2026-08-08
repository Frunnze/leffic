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
from sqlalchemy.orm import Session

from features.authentication.access import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from features.authentication.models import User
from features.authentication.schemas import UserCreate, UserLogin
from shared.database import get_db

auth = APIRouter()

DatabaseSession = Annotated[Session, Depends(get_db)]

_ISSUER = "my-issuer"
_REFRESH_COOKIE = "refresh_token"
_INVALID_CREDENTIALS = "Invalid token"


def _issue_refresh_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
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
    user: UserCreate, response: Response, db: DatabaseSession
) -> JSONResponse | dict[str, str]:
    # Check if username or email already exists
    if db.query(User).filter(User.username == user.username).first():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content="Username already registered",
        )

    if db.query(User).filter(User.email == user.email).first():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content="Email already registered",
        )

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_id = str(db_user.id)

    # Set the refresh token in the HTTP-only cookie
    _issue_refresh_cookie(response, user_id)

    # Return response with tokens and user
    return _session_payload(
        db_user,
        create_access_token(data={"user_id": user_id, "iss": _ISSUER}),
    )


@auth.post("/login", response_model=None)
def login_user(
    user_login: UserLogin, response: Response, db: DatabaseSession
) -> JSONResponse | dict[str, str]:
    # Find user by email
    user = db.query(User).filter(User.email == user_login.email).first()

    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Incorrect email"},
        )

    # Verify password
    if not verify_password(user_login.password, user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Incorrect password"},
        )

    user_id = str(user.id)

    # Set the refresh token in the HTTP-only cookie
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
        path="/",
    )
    response.status_code = status.HTTP_200_OK

    return {"message": "Successfully logged out"}
