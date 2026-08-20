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
from shared.folder_access import resolved_folder_id
from shared.models import File as StoredFile
from shared.models import Folder
from shared.pdf_conversion import ConversionError, PdfConversion

file_uploader = APIRouter()

_FILES_DIRECTORY = "files"
_HOME_FOLDER = "home"
_PDF_EXTENSION = "pdf"
_PDF_MEDIA_TYPE = "application/pdf"
_FILE_NOT_FOUND = "File not found"
_MISSING_FILE = "File does not exist!"
_MISSING_FOLDER = "Folder does not exist!"

UploadedFiles = Annotated[list[UploadFile], File(...)]
FolderId = Annotated[str | None, Form(...)]


def save_file_to_storage(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def _stored_file(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def _recorded_files(
    db: Session, folder_id: str, uploaded_files: list[dict[str, str]]
) -> None:
    folder = db.query(Folder).filter_by(id=folder_id).first()

    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FOLDER
        )

    for uploaded in uploaded_files:
        folder.files.append(
            StoredFile(
                id=uuid.UUID(uploaded["file_id"]),
                name=uploaded["name"],
                extension=uploaded["extension"],
            )
        )

    db.commit()


@file_uploader.post("/upload-files")
async def upload_files(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    files: UploadedFiles,
    folder_id: FolderId = None,
) -> dict[str, object]:
    uploaded_files = [_stored_file(file) for file in files]
    _recorded_files(db, resolved_folder_id(user_id, folder_id), uploaded_files)

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
