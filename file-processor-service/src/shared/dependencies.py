from typing import Annotated

from fastapi import Depends

from shared.claims_extractor import get_user_id_from_jwt

AuthenticatedUserId = Annotated[str, Depends(get_user_id_from_jwt)]
