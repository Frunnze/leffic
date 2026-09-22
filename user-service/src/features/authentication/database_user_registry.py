from typing import Annotated, override

from fastapi import Depends
from sqlalchemy.orm import Session

from features.authentication.user_registry import UserRegistry
from shared.database import get_db
from shared.models import User

DatabaseSession = Annotated[Session, Depends(get_db)]


class DatabaseUserRegistry(UserRegistry):
    def __init__(self, session: DatabaseSession) -> None:
        self._session: Session = session

    @override
    def user_named(self, username: str) -> User | None:
        return (
            self._session.query(User)
            .filter(User.username == username)
            .first()
        )

    @override
    def user_with_email(self, email: str) -> User | None:
        return self._session.query(User).filter(User.email == email).first()

    @override
    def register(self, user: User) -> None:
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
