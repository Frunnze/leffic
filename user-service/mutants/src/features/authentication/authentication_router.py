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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__issue_refresh_cookie__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__issue_refresh_cookie__mutmut)
def _issue_refresh_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_orig(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_1(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=None,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_2(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=None,
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_3(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=None,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_4(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite=None,
    )


def x__issue_refresh_cookie__mutmut_5(response: Response, user_id: str) -> None:
    response.set_cookie(
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_6(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_7(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_8(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        )


def x__issue_refresh_cookie__mutmut_9(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data=None
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_10(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"XXuser_idXX": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_11(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"USER_ID": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_12(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "XXissXX": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_13(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "ISS": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_14(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=False,  # Prevent JavaScript access
        samesite="strict",
    )


def x__issue_refresh_cookie__mutmut_15(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="XXstrictXX",
    )


def x__issue_refresh_cookie__mutmut_16(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=create_refresh_token(
            data={"user_id": user_id, "iss": _ISSUER}
        ),
        httponly=True,  # Prevent JavaScript access
        samesite="STRICT",
    )

mutants_x__issue_refresh_cookie__mutmut['_mutmut_orig'] = x__issue_refresh_cookie__mutmut_orig # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_1'] = x__issue_refresh_cookie__mutmut_1 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_2'] = x__issue_refresh_cookie__mutmut_2 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_3'] = x__issue_refresh_cookie__mutmut_3 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_4'] = x__issue_refresh_cookie__mutmut_4 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_5'] = x__issue_refresh_cookie__mutmut_5 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_6'] = x__issue_refresh_cookie__mutmut_6 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_7'] = x__issue_refresh_cookie__mutmut_7 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_8'] = x__issue_refresh_cookie__mutmut_8 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_9'] = x__issue_refresh_cookie__mutmut_9 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_10'] = x__issue_refresh_cookie__mutmut_10 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_11'] = x__issue_refresh_cookie__mutmut_11 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_12'] = x__issue_refresh_cookie__mutmut_12 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_13'] = x__issue_refresh_cookie__mutmut_13 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_14'] = x__issue_refresh_cookie__mutmut_14 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_15'] = x__issue_refresh_cookie__mutmut_15 # type: ignore # mutmut generated
mutants_x__issue_refresh_cookie__mutmut['x__issue_refresh_cookie__mutmut_16'] = x__issue_refresh_cookie__mutmut_16 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__session_payload__mutmut)
def _session_payload(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_orig(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_1(user: User, access_token: str) -> dict[str, str]:
    return {
        "XXuser_idXX": str(user.id),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_2(user: User, access_token: str) -> dict[str, str]:
    return {
        "USER_ID": str(user.id),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_3(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(None),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_4(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "XXusernameXX": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_5(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "USERNAME": user.username,
        "email": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_6(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "XXemailXX": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_7(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "EMAIL": user.email,
        "access_token": access_token,
    }


def x__session_payload__mutmut_8(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "XXaccess_tokenXX": access_token,
    }


def x__session_payload__mutmut_9(user: User, access_token: str) -> dict[str, str]:
    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "ACCESS_TOKEN": access_token,
    }

mutants_x__session_payload__mutmut['_mutmut_orig'] = x__session_payload__mutmut_orig # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_1'] = x__session_payload__mutmut_1 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_2'] = x__session_payload__mutmut_2 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_3'] = x__session_payload__mutmut_3 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_4'] = x__session_payload__mutmut_4 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_5'] = x__session_payload__mutmut_5 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_6'] = x__session_payload__mutmut_6 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_7'] = x__session_payload__mutmut_7 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_8'] = x__session_payload__mutmut_8 # type: ignore # mutmut generated
mutants_x__session_payload__mutmut['x__session_payload__mutmut_9'] = x__session_payload__mutmut_9 # type: ignore # mutmut generated


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
mutants_x__refreshed_user_id__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__refreshed_user_id__mutmut)
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


def x__refreshed_user_id__mutmut_orig(token: str) -> str:
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


def x__refreshed_user_id__mutmut_1(token: str) -> str:
    try:
        claims = None
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


def x__refreshed_user_id__mutmut_2(token: str) -> str:
    try:
        claims = jwt.decode(None, SECRET_KEY, algorithms=[ALGORITHM])
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


def x__refreshed_user_id__mutmut_3(token: str) -> str:
    try:
        claims = jwt.decode(token, None, algorithms=[ALGORITHM])
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


def x__refreshed_user_id__mutmut_4(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=None)
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


def x__refreshed_user_id__mutmut_5(token: str) -> str:
    try:
        claims = jwt.decode(SECRET_KEY, algorithms=[ALGORITHM])
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


def x__refreshed_user_id__mutmut_6(token: str) -> str:
    try:
        claims = jwt.decode(token, algorithms=[ALGORITHM])
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


def x__refreshed_user_id__mutmut_7(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, )
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


def x__refreshed_user_id__mutmut_8(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=None,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_9(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=None,
        ) from error

    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_10(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_11(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            ) from error

    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_12(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = None

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_13(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get(None)

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_14(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get("XXuser_idXX")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_15(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get("USER_ID")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_16(token: str) -> str:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        ) from error

    user_id = claims.get("user_id")

    if isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_17(token: str) -> str:
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
            status_code=None,
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_18(token: str) -> str:
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
            detail=None,
        )

    return user_id


def x__refreshed_user_id__mutmut_19(token: str) -> str:
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
            detail=_INVALID_CREDENTIALS,
        )

    return user_id


def x__refreshed_user_id__mutmut_20(token: str) -> str:
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
            )

    return user_id

mutants_x__refreshed_user_id__mutmut['_mutmut_orig'] = x__refreshed_user_id__mutmut_orig # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_1'] = x__refreshed_user_id__mutmut_1 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_2'] = x__refreshed_user_id__mutmut_2 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_3'] = x__refreshed_user_id__mutmut_3 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_4'] = x__refreshed_user_id__mutmut_4 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_5'] = x__refreshed_user_id__mutmut_5 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_6'] = x__refreshed_user_id__mutmut_6 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_7'] = x__refreshed_user_id__mutmut_7 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_8'] = x__refreshed_user_id__mutmut_8 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_9'] = x__refreshed_user_id__mutmut_9 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_10'] = x__refreshed_user_id__mutmut_10 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_11'] = x__refreshed_user_id__mutmut_11 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_12'] = x__refreshed_user_id__mutmut_12 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_13'] = x__refreshed_user_id__mutmut_13 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_14'] = x__refreshed_user_id__mutmut_14 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_15'] = x__refreshed_user_id__mutmut_15 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_16'] = x__refreshed_user_id__mutmut_16 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_17'] = x__refreshed_user_id__mutmut_17 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_18'] = x__refreshed_user_id__mutmut_18 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_19'] = x__refreshed_user_id__mutmut_19 # type: ignore # mutmut generated
mutants_x__refreshed_user_id__mutmut['x__refreshed_user_id__mutmut_20'] = x__refreshed_user_id__mutmut_20 # type: ignore # mutmut generated


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
