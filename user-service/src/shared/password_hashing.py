from typing import Annotated

from passlib.context import CryptContext
from passlib.exc import PasswordValueError
from pydantic import AfterValidator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_NUL_BYTE = "\x00"
_NUL_REFUSAL = "A password cannot contain a NUL byte."


def storable_password(password: str) -> str:
    if _NUL_BYTE in password:
        raise ValueError(_NUL_REFUSAL)

    return password


Password = Annotated[str, AfterValidator(storable_password)]


def hash_password(password: str) -> str:
    return str(pwd_context.hash(storable_password(password)))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bool(pwd_context.verify(plain_password, hashed_password))
    except PasswordValueError:
        return False
