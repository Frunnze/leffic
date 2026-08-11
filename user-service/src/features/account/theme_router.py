from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from features.account.account_lookup import account
from shared.claims_extractor import get_user_id_from_jwt
from shared.database import get_db

theme_router = APIRouter(prefix="/account")

DatabaseSession = Annotated[Session, Depends(get_db)]
AuthenticatedUserId = Annotated[str, Depends(get_user_id_from_jwt)]


class ThemeRequest(BaseModel):
    theme: Literal["system", "light", "dark"]


@theme_router.patch("/theme")
async def choose_theme(
    request_data: ThemeRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    user = account(db, user_id)
    user.theme = request_data.theme
    db.commit()

    return JSONResponse(content={"theme": user.theme})
