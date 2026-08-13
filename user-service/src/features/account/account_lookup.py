import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from shared.models import User
from shared.password_hashing import verify_password

_MISSING_ACCOUNT = "Account does not exist!"
_WRONG_CREDENTIALS = "That password is not right."


def account(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_ACCOUNT
        )

    return user


def confirmed_account(db: Session, user_id: str, password: str) -> User:
    user = account(db, user_id)

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_WRONG_CREDENTIALS,
        )

    return user
