import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from features.account import key_sealing
from features.account.account_lookup import confirmed_account
from features.account.claims_extractor import get_user_id_from_jwt
from features.account.models import ProviderKey
from shared.database import get_db
from shared.password_hashing import Password

provider_key_router = APIRouter(prefix="/account/provider-keys")

DatabaseSession = Annotated[Session, Depends(get_db)]
AuthenticatedUserId = Annotated[str, Depends(get_user_id_from_jwt)]

_SUPPORTED_PROVIDERS = ("openai", "gemini")
_UNKNOWN_PROVIDER = "That AI provider is not supported."
_BLANK_KEY = "The key cannot be blank."
_MISSING_KEY = "No key is saved for that provider."
_SEALED_BEFORE = "This key was sealed with an earlier password."


class ProviderKeyRequest(BaseModel):
    provider: str
    key: str
    password: Password
    monthly_limit_cents: int | None = None


def _keys_of(db: Session, user_id: str) -> list[ProviderKey]:
    return (
        db.query(ProviderKey)
        .filter(ProviderKey.user_id == uuid.UUID(user_id))
        .all()
    )


@provider_key_router.get("")
async def read_provider_keys(
    user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    return JSONResponse(
        content={
            "provider_keys": [
                {
                    "provider": saved_key.provider,
                    "hint": saved_key.hint,
                    "monthly_limit_cents": saved_key.monthly_limit_cents,
                    "spent_cents": saved_key.spent_cents,
                }
                for saved_key in _keys_of(db, user_id)
            ]
        }
    )


@provider_key_router.put("")
async def save_provider_key(
    request_data: ProviderKeyRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    if request_data.provider not in _SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_UNKNOWN_PROVIDER,
        )

    key = request_data.key.strip()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_BLANK_KEY,
        )

    _ = confirmed_account(db, user_id, request_data.password)
    salt = key_sealing.new_salt()
    sealed = key_sealing.seal(key, request_data.password, salt)
    hint = key_sealing.hint_for(key)
    existing = _saved_key(db, user_id, request_data.provider)

    if existing is None:
        db.add(
            ProviderKey(
                user_id=uuid.UUID(user_id),
                provider=request_data.provider,
                sealed_key=sealed,
                salt=salt,
                hint=hint,
                monthly_limit_cents=request_data.monthly_limit_cents,
                spent_cents=0,
            )
        )
    else:
        existing.sealed_key = sealed
        existing.salt = salt
        existing.hint = hint
        existing.monthly_limit_cents = request_data.monthly_limit_cents

    db.commit()

    return JSONResponse(content={"hint": hint})


class OpenKeyRequest(BaseModel):
    password: Password


@provider_key_router.post("/{provider}/open")
async def open_provider_key(
    provider: str,
    request_data: OpenKeyRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    _ = confirmed_account(db, user_id, request_data.password)
    saved_key = _saved_key(db, user_id, provider)

    if saved_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_KEY
        )

    opened = key_sealing.unseal(
        saved_key.sealed_key, request_data.password, saved_key.salt
    )

    if opened is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_SEALED_BEFORE
        )

    return JSONResponse(content={"key": opened})


def _saved_key(
    db: Session, user_id: str, provider: str
) -> ProviderKey | None:
    return (
        db.query(ProviderKey)
        .filter(
            ProviderKey.user_id == uuid.UUID(user_id),
            ProviderKey.provider == provider,
        )
        .first()
    )


@provider_key_router.delete("/{provider}")
async def delete_provider_key(
    provider: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    saved_key = _saved_key(db, user_id, provider)

    if saved_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_KEY
        )

    db.delete(saved_key)
    db.commit()

    return JSONResponse(content={"msg": "Key removed!"})
