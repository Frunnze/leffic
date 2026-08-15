import uuid
from typing import Annotated

from fastapi import HTTPException, status
from pydantic import Field

_LARGEST_ROW_ID = 2**31 - 1

RowId = Annotated[int, Field(ge=1, le=_LARGEST_ROW_ID)]


def parsed_identifier(
    identifier_text: str, missing_detail: str
) -> uuid.UUID:
    try:
        return uuid.UUID(identifier_text)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=missing_detail
        ) from None
