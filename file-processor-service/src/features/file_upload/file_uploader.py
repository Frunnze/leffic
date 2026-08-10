import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response

from features.file_upload.content_client import register_files
from shared.dependencies import AuthenticatedUserId

file_uploader = APIRouter()

_FILES_DIRECTORY = "files"
_HOME_FOLDER = "home"
_PDF_EXTENSION = "pdf"
_PDF_MEDIA_TYPE = "application/pdf"
_FILE_NOT_FOUND = "File not found"
_CONVERSION_TIMEOUT_SECONDS = 120

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


@file_uploader.post("/upload-files")
async def upload_files(
    user_id: AuthenticatedUserId,
    files: UploadedFiles,
    folder_id: FolderId = None,
) -> dict[str, object]:
    resolved_folder_id = (
        user_id if folder_id == _HOME_FOLDER else folder_id
    )
    uploaded_files = [_stored_file(file) for file in files]

    register_files(uploaded_files, resolved_folder_id)

    return {"msg": "Files uploaded!", "file_metadata": uploaded_files}


@file_uploader.get("/file")
async def get_file(file_id: str, file_extension: str) -> Response:
    input_path = Path(_FILES_DIRECTORY) / f"{file_id}.{file_extension}"

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
        content=_converted_to_pdf(input_path, file_id),
        media_type=_PDF_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f"attachment; filename={file_id}.{_PDF_EXTENSION}"
            )
        },
    )


def _converted_to_pdf(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                _PDF_EXTENSION,
                "--outdir",
                tmp_dir,
                str(input_path),
            ],
            capture_output=True,
            check=False,
            timeout=_CONVERSION_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()
