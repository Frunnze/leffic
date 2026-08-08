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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_hash_password__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_hash_password__mutmut)
def hash_password(password: str) -> str:
    return str(pwd_context.hash(password))


def x_hash_password__mutmut_orig(password: str) -> str:
    return str(pwd_context.hash(password))


def x_hash_password__mutmut_1(password: str) -> str:
    return str(None)


def x_hash_password__mutmut_2(password: str) -> str:
    return str(pwd_context.hash(None))

mutants_x_hash_password__mutmut['_mutmut_orig'] = x_hash_password__mutmut_orig # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_1'] = x_hash_password__mutmut_1 # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_2'] = x_hash_password__mutmut_2 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_verify_password__mutmut)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def x_verify_password__mutmut_orig(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def x_verify_password__mutmut_1(plain_password: str, hashed_password: str) -> bool:
    return bool(None)


def x_verify_password__mutmut_2(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(None, hashed_password))


def x_verify_password__mutmut_3(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, None))


def x_verify_password__mutmut_4(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(hashed_password))


def x_verify_password__mutmut_5(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, ))

mutants_x_verify_password__mutmut['_mutmut_orig'] = x_verify_password__mutmut_orig # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_1'] = x_verify_password__mutmut_1 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_2'] = x_verify_password__mutmut_2 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_3'] = x_verify_password__mutmut_3 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_4'] = x_verify_password__mutmut_4 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_5'] = x_verify_password__mutmut_5 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_create_access_token__mutmut)
def create_access_token(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_orig(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_1(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = None
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_2(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(None)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_3(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = None
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_4(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) - (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_5(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(None) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_6(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta and timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_7(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=None)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_8(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = None

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_9(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["XXexpXX"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_10(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["EXP"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_access_token__mutmut_11(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(None, SECRET_KEY)


def x_create_access_token__mutmut_12(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, None)


def x_create_access_token__mutmut_13(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(SECRET_KEY)


def x_create_access_token__mutmut_14(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, )

mutants_x_create_access_token__mutmut['_mutmut_orig'] = x_create_access_token__mutmut_orig # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_1'] = x_create_access_token__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_2'] = x_create_access_token__mutmut_2 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_3'] = x_create_access_token__mutmut_3 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_4'] = x_create_access_token__mutmut_4 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_5'] = x_create_access_token__mutmut_5 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_6'] = x_create_access_token__mutmut_6 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_7'] = x_create_access_token__mutmut_7 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_8'] = x_create_access_token__mutmut_8 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_9'] = x_create_access_token__mutmut_9 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_10'] = x_create_access_token__mutmut_10 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_11'] = x_create_access_token__mutmut_11 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_12'] = x_create_access_token__mutmut_12 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_13'] = x_create_access_token__mutmut_13 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_14'] = x_create_access_token__mutmut_14 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_create_refresh_token__mutmut)
def create_refresh_token(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_orig(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_1(data: dict[str, str]) -> str:
    expire = None
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_2(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) - timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_3(data: dict[str, str]) -> str:
    expire = datetime.now(None) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_4(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=None)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_5(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = None
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_6(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(None)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_7(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = None

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_8(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["XXexpXX"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_9(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["EXP"] = expire

    return jwt.encode(to_encode, SECRET_KEY)


def x_create_refresh_token__mutmut_10(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(None, SECRET_KEY)


def x_create_refresh_token__mutmut_11(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, None)


def x_create_refresh_token__mutmut_12(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(SECRET_KEY)


def x_create_refresh_token__mutmut_13(data: dict[str, str]) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: dict[str, object] = dict(data)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, )

mutants_x_create_refresh_token__mutmut['_mutmut_orig'] = x_create_refresh_token__mutmut_orig # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_1'] = x_create_refresh_token__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_2'] = x_create_refresh_token__mutmut_2 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_3'] = x_create_refresh_token__mutmut_3 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_4'] = x_create_refresh_token__mutmut_4 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_5'] = x_create_refresh_token__mutmut_5 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_6'] = x_create_refresh_token__mutmut_6 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_7'] = x_create_refresh_token__mutmut_7 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_8'] = x_create_refresh_token__mutmut_8 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_9'] = x_create_refresh_token__mutmut_9 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_10'] = x_create_refresh_token__mutmut_10 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_11'] = x_create_refresh_token__mutmut_11 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_12'] = x_create_refresh_token__mutmut_12 # type: ignore # mutmut generated
mutants_x_create_refresh_token__mutmut['x_create_refresh_token__mutmut_13'] = x_create_refresh_token__mutmut_13 # type: ignore # mutmut generated
