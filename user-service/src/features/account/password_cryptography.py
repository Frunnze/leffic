from abc import ABC, abstractmethod


class PasswordCryptography(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str: ...

    @abstractmethod
    def verify_password(
        self, password: str, hashed_password: str
    ) -> bool: ...

    @abstractmethod
    def seal_key(self, key: str, password: str, salt: str) -> str: ...

    @abstractmethod
    def open_key(
        self, sealed_key: str, password: str, salt: str
    ) -> str | None: ...
