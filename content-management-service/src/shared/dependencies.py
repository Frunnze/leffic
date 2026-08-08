from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.shared.claims_extractor import get_user_id_from_jwt
from src.shared.database import get_db

DatabaseSession = Annotated[Session, Depends(get_db)]
AuthenticatedUserId = Annotated[str, Depends(get_user_id_from_jwt)]
