from typing import Annotated

import jwt
from fastapi import Header, HTTPException, status

_BEARER_SCHEME = "bearer"
_BEARER_HEADER_PARTS = 2
_MISSING_USER_ID = "Token carries no user_id"
_MISSING_SCHEME = "Invalid token: expected a bearer scheme"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_user_id_from_jwt__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_user_id_from_jwt__mutmut)
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


def x_get_user_id_from_jwt__mutmut_orig(
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


def x_get_user_id_from_jwt__mutmut_1(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = None
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_2(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(None)
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_3(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = None

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_4(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get(None)

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_5(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("XXuser_idXX")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_6(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("USER_ID")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_7(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("user_id")

    if isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_8(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=None,
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_9(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=None,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_10(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            detail=_MISSING_USER_ID,
        )

    return user_id


def x_get_user_id_from_jwt__mutmut_11(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    claims = _decode_claims(authorization)
    user_id = claims.get("user_id")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            )

    return user_id

mutants_x_get_user_id_from_jwt__mutmut['_mutmut_orig'] = x_get_user_id_from_jwt__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_1'] = x_get_user_id_from_jwt__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_2'] = x_get_user_id_from_jwt__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_3'] = x_get_user_id_from_jwt__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_4'] = x_get_user_id_from_jwt__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_5'] = x_get_user_id_from_jwt__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_6'] = x_get_user_id_from_jwt__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_7'] = x_get_user_id_from_jwt__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_8'] = x_get_user_id_from_jwt__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_9'] = x_get_user_id_from_jwt__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_10'] = x_get_user_id_from_jwt__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_user_id_from_jwt__mutmut['x_get_user_id_from_jwt__mutmut_11'] = x_get_user_id_from_jwt__mutmut_11 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__decode_claims__mutmut)
def _decode_claims(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_orig(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_1(authorization: str | None) -> dict[str, object]:
    token = None

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_2(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(None)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_3(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(None, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_4(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options=None)
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_5(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_6(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, )
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_7(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"XXverify_signatureXX": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_8(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"VERIFY_SIGNATURE": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_9(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": True})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_10(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=None,
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_11(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=None,
        ) from error


def x__decode_claims__mutmut_12(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            detail=f"Invalid token: {error}",
        ) from error


def x__decode_claims__mutmut_13(authorization: str | None) -> dict[str, object]:
    token = _bearer_token(authorization)

    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            ) from error

mutants_x__decode_claims__mutmut['_mutmut_orig'] = x__decode_claims__mutmut_orig # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_1'] = x__decode_claims__mutmut_1 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_2'] = x__decode_claims__mutmut_2 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_3'] = x__decode_claims__mutmut_3 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_4'] = x__decode_claims__mutmut_4 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_5'] = x__decode_claims__mutmut_5 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_6'] = x__decode_claims__mutmut_6 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_7'] = x__decode_claims__mutmut_7 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_8'] = x__decode_claims__mutmut_8 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_9'] = x__decode_claims__mutmut_9 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_10'] = x__decode_claims__mutmut_10 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_11'] = x__decode_claims__mutmut_11 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_12'] = x__decode_claims__mutmut_12 # type: ignore # mutmut generated
mutants_x__decode_claims__mutmut['x__decode_claims__mutmut_13'] = x__decode_claims__mutmut_13 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__bearer_token__mutmut)
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


def x__bearer_token__mutmut_orig(authorization: str | None) -> str:
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


def x__bearer_token__mutmut_1(authorization: str | None) -> str:
    if authorization is not None:
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


def x__bearer_token__mutmut_2(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=None,
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


def x__bearer_token__mutmut_3(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=None,
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


def x__bearer_token__mutmut_4(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
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


def x__bearer_token__mutmut_5(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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


def x__bearer_token__mutmut_6(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = None

    if (
        len(parts) != _BEARER_HEADER_PARTS
        or parts[0].lower() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_7(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = authorization.split()

    if (
        len(parts) != _BEARER_HEADER_PARTS and parts[0].lower() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_8(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = authorization.split()

    if (
        len(parts) == _BEARER_HEADER_PARTS
        or parts[0].lower() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_9(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = authorization.split()

    if (
        len(parts) != _BEARER_HEADER_PARTS
        or parts[0].upper() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_10(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = authorization.split()

    if (
        len(parts) != _BEARER_HEADER_PARTS
        or parts[1].lower() != _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_11(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    parts = authorization.split()

    if (
        len(parts) != _BEARER_HEADER_PARTS
        or parts[0].lower() == _BEARER_SCHEME
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_12(authorization: str | None) -> str:
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
            status_code=None,
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_13(authorization: str | None) -> str:
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
            detail=None,
        )

    return parts[1]


def x__bearer_token__mutmut_14(authorization: str | None) -> str:
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
            detail=_MISSING_SCHEME,
        )

    return parts[1]


def x__bearer_token__mutmut_15(authorization: str | None) -> str:
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
            )

    return parts[1]


def x__bearer_token__mutmut_16(authorization: str | None) -> str:
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

    return parts[2]

mutants_x__bearer_token__mutmut['_mutmut_orig'] = x__bearer_token__mutmut_orig # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_1'] = x__bearer_token__mutmut_1 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_2'] = x__bearer_token__mutmut_2 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_3'] = x__bearer_token__mutmut_3 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_4'] = x__bearer_token__mutmut_4 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_5'] = x__bearer_token__mutmut_5 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_6'] = x__bearer_token__mutmut_6 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_7'] = x__bearer_token__mutmut_7 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_8'] = x__bearer_token__mutmut_8 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_9'] = x__bearer_token__mutmut_9 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_10'] = x__bearer_token__mutmut_10 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_11'] = x__bearer_token__mutmut_11 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_12'] = x__bearer_token__mutmut_12 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_13'] = x__bearer_token__mutmut_13 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_14'] = x__bearer_token__mutmut_14 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_15'] = x__bearer_token__mutmut_15 # type: ignore # mutmut generated
mutants_x__bearer_token__mutmut['x__bearer_token__mutmut_16'] = x__bearer_token__mutmut_16 # type: ignore # mutmut generated
