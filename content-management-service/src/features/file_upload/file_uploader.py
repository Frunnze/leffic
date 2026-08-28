import shutil
import uuid
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from shared.content_access import owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.file_storage import delete_file_from_storage, storage_name
from shared.folder_access import owned_folder_id
from shared.models import File as StoredFile
from shared.pdf_conversion import ConversionError, PdfConversion

file_uploader = APIRouter()

UploadedFileMetadata = dict[str, str]

_FILES_DIRECTORY = "files"
_PDF_EXTENSION = "pdf"
_PDF_MEDIA_TYPE = "application/pdf"
_FILE_NOT_FOUND = "File not found"
_MISSING_FILE = "File does not exist!"
_MAXIMUM_STORAGE_NAME_BYTES = 255

UploadedFiles = Annotated[list[UploadFile], File(...)]
FolderId = Annotated[str | None, Form(...)]


def save_file_to_storage(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def _uploaded_file_metadata(file: UploadFile) -> UploadedFileMetadata:
    filename = file.filename or ""

    return {
        "file_id": str(uuid4()),
        "extension": Path(filename).suffix.lstrip("."),
        "name": filename,
    }


def _remove_uploaded_files_from_storage(
    uploaded_files: list[UploadedFileMetadata],
) -> None:
    for uploaded_file_metadata in uploaded_files:
        stored_name = storage_name(
            uploaded_file_metadata["file_id"],
            uploaded_file_metadata["extension"],
        )

        name_length_in_bytes = len(stored_name.encode())

        if name_length_in_bytes <= _MAXIMUM_STORAGE_NAME_BYTES:
            delete_file_from_storage(stored_name)


def _recorded_files(
    db: Session,
    folder_id: str,
    uploaded_files: list[UploadedFileMetadata],
) -> None:
    db.add_all(
        [
            StoredFile(
                id=uuid.UUID(uploaded_file_metadata["file_id"]),
                name=uploaded_file_metadata["name"],
                extension=uploaded_file_metadata["extension"],
                folder_id=folder_id,
            )
            for uploaded_file_metadata in uploaded_files
        ]
    )

    db.commit()


@file_uploader.post("/upload-files")
async def upload_files(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    files: UploadedFiles,
    folder_id: FolderId = None,
) -> dict[str, object]:
    owned_folder_identifier = owned_folder_id(db, user_id, folder_id)
    uploaded_files: list[UploadedFileMetadata] = []

    try:
        for file in files:
            uploaded_file_metadata = _uploaded_file_metadata(file)
            uploaded_files.append(uploaded_file_metadata)
            save_file_to_storage(
                file,
                storage_name(
                    uploaded_file_metadata["file_id"],
                    uploaded_file_metadata["extension"],
                ),
            )

        _recorded_files(db, owned_folder_identifier, uploaded_files)
    except BaseException:
        _remove_uploaded_files_from_storage(uploaded_files)
        raise

    return {"msg": "Files uploaded!", "file_metadata": uploaded_files}


@file_uploader.get("/file")
async def get_file(
    file_id: str,
    file_extension: str,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> Response:
    owned = owned_content(db, user_id, StoredFile, file_id, _MISSING_FILE)
    input_path = Path(_FILES_DIRECTORY) / f"{owned.id}.{file_extension}"

    if not input_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_FILE_NOT_FOUND
        )

    if file_extension == _PDF_EXTENSION:
        return FileResponse(
            path=input_path,
            media_type=_PDF_MEDIA_TYPE,
            filename=f"{file_id}.{_PDF_EXTENSION}",
        )

    return Response(
        content=_converted_to_pdf(input_path, file_extension),
        media_type=_PDF_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f"attachment; filename={file_id}.{_PDF_EXTENSION}"
            )
        },
    )


def _converted_to_pdf(input_path: Path, file_extension: str) -> bytes:
    try:
        return PdfConversion.converted(input_path.read_bytes(), file_extension)
    except ConversionError as failure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conversion failed: {failure}",
        ) from failure
