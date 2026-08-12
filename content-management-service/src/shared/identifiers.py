import uuid

from fastapi import HTTPException, status


def parsed_identifier(
    identifier_text: str, missing_detail: str
) -> uuid.UUID:
    try:
        return uuid.UUID(identifier_text)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=missing_detail
        ) from None
