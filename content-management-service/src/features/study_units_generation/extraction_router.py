from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.study_units_generation.pdf_pages import PageSelectionError
from features.study_units_generation.text_sources import (
    FileMetadata,
    MissingDocumentError,
    text_from_files,
    text_from_link,
)
from shared.dependencies import AuthenticatedUserId
from shared.pdf_conversion import ConversionError

extraction_router = APIRouter()

_NO_TEXT = "Could not extract text!"
_TOPIC_IS_WRITTEN = "A topic is written into a note, not extracted."


class ExtractionRequest(BaseModel):
    file_metadata: list[FileMetadata] | None = None
    link_metadata: str | None = None
    topic_metadata: str | None = None


def _extracted_text(request_data: ExtractionRequest) -> str:
    if request_data.file_metadata:
        return text_from_files(request_data.file_metadata)

    if request_data.link_metadata:
        return text_from_link(request_data.link_metadata)

    return ""


@extraction_router.post("/extract-text", response_model=None)
async def extract_text(
    request_data: ExtractionRequest, user_id: AuthenticatedUserId
) -> dict[str, str] | JSONResponse:
    _ = user_id

    if request_data.topic_metadata:
        return JSONResponse(
            content={"msg": _TOPIC_IS_WRITTEN},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        extracted_text = _extracted_text(request_data)
    except (
        PageSelectionError,
        ConversionError,
        MissingDocumentError,
    ) as refusal:
        return JSONResponse(
            content={"msg": str(refusal)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not extracted_text:
        return JSONResponse(
            content={"msg": _NO_TEXT},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return {"text": extracted_text}
