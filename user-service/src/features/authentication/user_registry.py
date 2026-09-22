from abc import ABC, abstractmethod

from shared.models import User


class UserRegistry(ABC):
    @abstractmethod
    def user_named(self, username: str) -> User | None: ...

    @abstractmethod
    def user_with_email(self, email: str) -> User | None: ...

    @abstractmethod
    def register(self, user: User) -> None: ...
