from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from features.study_units_generation.pdf_pages import PageSelectionError
from features.study_units_generation.text_sources import (
    FileMetadata,
    MissingDocumentError,
    StoredDocument,
    text_from_files,
    text_from_link,
)
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.file_access import owned_file
from shared.file_storage import storage_name
from shared.pdf_conversion import ConversionError

extraction_router = APIRouter()

_NO_TEXT = "Could not extract text!"
_TOPIC_IS_WRITTEN = "A topic is written into a note, not extracted."


class ExtractionRequest(BaseModel):
    file_metadata: list[FileMetadata] | None = None
    link_metadata: str | None = None
    topic_metadata: str | None = None


def _resolved_documents(
    db: Session, user_id: str, file_metadata: list[FileMetadata]
) -> list[StoredDocument]:
    documents: list[StoredDocument] = []

    for requested_document in file_metadata:
        owned_file_record = owned_file(
            db, user_id, requested_document.file_id
        )
        documents.append(
            StoredDocument(
                storage_name=storage_name(
                    str(owned_file_record.id), owned_file_record.extension
                ),
                extension=owned_file_record.extension,
                pages=requested_document.pages,
            )
        )

    return documents


def _extracted_text(
    documents: list[StoredDocument], link: str | None
) -> str:
    if documents:
        return text_from_files(documents)

    if link:
        return text_from_link(link)

    return ""


@extraction_router.post("/extract-text", response_model=None)
async def extract_text(
    request_data: ExtractionRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> dict[str, str] | JSONResponse:
    if request_data.topic_metadata:
        return JSONResponse(
            content={"msg": _TOPIC_IS_WRITTEN},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    documents = _resolved_documents(
        db, user_id, request_data.file_metadata or []
    )

    try:
        extracted_text = _extracted_text(
            documents, request_data.link_metadata
        )
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
