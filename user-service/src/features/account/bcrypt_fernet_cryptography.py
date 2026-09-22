from typing import override

from features.account import key_sealing
from features.account.password_cryptography import PasswordCryptography
from shared import password_hashing


class BcryptFernetCryptography(PasswordCryptography):
    @override
    def hash_password(self, password: str) -> str:
        return password_hashing.hash_password(password)

    @override
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return password_hashing.verify_password(password, hashed_password)

    @override
    def seal_key(self, key: str, password: str, salt: str) -> str:
        return key_sealing.seal(key, password, salt)

    @override
    def open_key(
        self, sealed_key: str, password: str, salt: str
    ) -> str | None:
        return key_sealing.unseal(sealed_key, password, salt)
