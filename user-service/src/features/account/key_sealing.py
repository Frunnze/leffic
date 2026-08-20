import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

_SALT_BYTES = 16
_SCRYPT_COST = 2**14
_SCRYPT_BLOCK_SIZE = 8
_SCRYPT_PARALLELISM = 1
_DERIVED_KEY_BYTES = 32
_HINT_CHARACTERS = 4


def new_salt() -> str:
    return base64.b64encode(os.urandom(_SALT_BYTES)).decode()


def seal(secret: str, password: str, salt: str) -> str:
    return Fernet(_derived_key(password, salt)).encrypt(
        secret.encode()
    ).decode()


def unseal(sealed_secret: str, password: str, salt: str) -> str | None:
    try:
        opened = Fernet(_derived_key(password, salt)).decrypt(
            sealed_secret.encode()
        )
    except InvalidToken:
        return None

    return opened.decode()


def hint_for(secret: str) -> str:
    return secret[-_HINT_CHARACTERS:]


def _derived_key(password: str, salt: str) -> bytes:
    derived = hashlib.scrypt(
        password.encode(),
        salt=base64.b64decode(salt),
        n=_SCRYPT_COST,
        r=_SCRYPT_BLOCK_SIZE,
        p=_SCRYPT_PARALLELISM,
        dklen=_DERIVED_KEY_BYTES,
    )

    return base64.urlsafe_b64encode(derived)
