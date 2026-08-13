from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from features.account.account_lookup import account, confirmed_account
from features.account.models import ProviderKey
from shared.claims_extractor import get_user_id_from_jwt
from shared.database import get_db
from shared.events import USER_DELETED, BrokerUnavailableError, publish
from shared.models import User
from shared.password_hashing import hash_password

account_router = APIRouter(prefix="/account")

DatabaseSession = Annotated[Session, Depends(get_db)]
AuthenticatedUserId = Annotated[str, Depends(get_user_id_from_jwt)]

_MINIMUM_PASSWORD_LENGTH = 4
_TAKEN_USERNAME = "That username is taken."
_BLANK_USERNAME = "Username cannot be blank."
_SHORT_NEW_CREDENTIALS = "The new password is too short."
_CLEANUP_UNAVAILABLE = "Deletion is unavailable right now. Try again."


class UsernameRequest(BaseModel):
    username: str


class PasswordRequest(BaseModel):
    current_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    password: str


@account_router.get("")
async def read_account(
    user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    user = account(db, user_id)

    return JSONResponse(
        content={
            "username": user.username,
            "email": user.email,
            "theme": user.theme,
        }
    )


@account_router.patch("/username")
async def change_username(
    request_data: UsernameRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    username = request_data.username.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_BLANK_USERNAME,
        )

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_TAKEN_USERNAME
        )

    user = account(db, user_id)
    user.username = username
    db.commit()

    return JSONResponse(content={"username": username})


@account_router.patch("/password")
async def change_password(
    request_data: PasswordRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    if len(request_data.new_password) < _MINIMUM_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_SHORT_NEW_CREDENTIALS,
        )

    user = confirmed_account(db, user_id, request_data.current_password)
    user.hashed_password = hash_password(request_data.new_password)
    db.commit()

    return JSONResponse(content={"msg": "Password changed!"})


@account_router.delete("")
async def delete_account(
    request_data: DeleteAccountRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    user = confirmed_account(db, user_id, request_data.password)

    _announce_deletion(user_id)

    keys = (
        db.query(ProviderKey)
        .filter(ProviderKey.user_id == user.id)
        .all()
    )

    for saved_key in keys:
        db.delete(saved_key)

    db.delete(user)
    db.commit()

    return JSONResponse(content={"msg": "Account deleted!"})


def _announce_deletion(user_id: str) -> None:
    try:
        publish(USER_DELETED, {"user_id": user_id})
    except BrokerUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_CLEANUP_UNAVAILABLE,
        ) from error
