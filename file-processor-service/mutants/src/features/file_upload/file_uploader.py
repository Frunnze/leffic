import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response

from features.study_units_generation.content_management_client import (
    save_study_unit,
)
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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_save_file_to_storage__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_save_file_to_storage__mutmut)
def save_file_to_storage(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_orig(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_1(file: UploadFile, unique_name: str) -> None:
    file_path = None

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_2(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) * unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_3(file: UploadFile, unique_name: str) -> None:
    file_path = Path(None) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_4(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open(None) as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_5(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("XXwbXX") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_6(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("WB") as out_file:
        shutil.copyfileobj(file.file, out_file)


def x_save_file_to_storage__mutmut_7(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(None, out_file)


def x_save_file_to_storage__mutmut_8(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, None)


def x_save_file_to_storage__mutmut_9(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(out_file)


def x_save_file_to_storage__mutmut_10(file: UploadFile, unique_name: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / unique_name

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, )

mutants_x_save_file_to_storage__mutmut['_mutmut_orig'] = x_save_file_to_storage__mutmut_orig # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_1'] = x_save_file_to_storage__mutmut_1 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_2'] = x_save_file_to_storage__mutmut_2 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_3'] = x_save_file_to_storage__mutmut_3 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_4'] = x_save_file_to_storage__mutmut_4 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_5'] = x_save_file_to_storage__mutmut_5 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_6'] = x_save_file_to_storage__mutmut_6 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_7'] = x_save_file_to_storage__mutmut_7 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_8'] = x_save_file_to_storage__mutmut_8 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_9'] = x_save_file_to_storage__mutmut_9 # type: ignore # mutmut generated
mutants_x_save_file_to_storage__mutmut['x_save_file_to_storage__mutmut_10'] = x_save_file_to_storage__mutmut_10 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__stored_file__mutmut)
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


def x__stored_file__mutmut_orig(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_1(file: UploadFile) -> dict[str, str]:
    filename = None
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_2(file: UploadFile) -> dict[str, str]:
    filename = file.filename and ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_3(file: UploadFile) -> dict[str, str]:
    filename = file.filename or "XXXX"
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_4(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = None
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_5(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(None)
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_6(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = None
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_7(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(None).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_8(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(None, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_9(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, None)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_10(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_11(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, )

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_12(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id - extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_13(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "XXfile_idXX": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_14(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "FILE_ID": file_id,
        "extension": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_15(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "XXextensionXX": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_16(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "EXTENSION": extension.lstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_17(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip(None),
        "name": filename,
    }


def x__stored_file__mutmut_18(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.rstrip("."),
        "name": filename,
    }


def x__stored_file__mutmut_19(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("XX.XX"),
        "name": filename,
    }


def x__stored_file__mutmut_20(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "XXnameXX": filename,
    }


def x__stored_file__mutmut_21(file: UploadFile) -> dict[str, str]:
    filename = file.filename or ""
    file_id = str(uuid4())
    extension = Path(filename).suffix
    save_file_to_storage(file, file_id + extension)

    return {
        "file_id": file_id,
        "extension": extension.lstrip("."),
        "NAME": filename,
    }

mutants_x__stored_file__mutmut['_mutmut_orig'] = x__stored_file__mutmut_orig # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_1'] = x__stored_file__mutmut_1 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_2'] = x__stored_file__mutmut_2 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_3'] = x__stored_file__mutmut_3 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_4'] = x__stored_file__mutmut_4 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_5'] = x__stored_file__mutmut_5 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_6'] = x__stored_file__mutmut_6 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_7'] = x__stored_file__mutmut_7 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_8'] = x__stored_file__mutmut_8 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_9'] = x__stored_file__mutmut_9 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_10'] = x__stored_file__mutmut_10 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_11'] = x__stored_file__mutmut_11 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_12'] = x__stored_file__mutmut_12 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_13'] = x__stored_file__mutmut_13 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_14'] = x__stored_file__mutmut_14 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_15'] = x__stored_file__mutmut_15 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_16'] = x__stored_file__mutmut_16 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_17'] = x__stored_file__mutmut_17 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_18'] = x__stored_file__mutmut_18 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_19'] = x__stored_file__mutmut_19 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_20'] = x__stored_file__mutmut_20 # type: ignore # mutmut generated
mutants_x__stored_file__mutmut['x__stored_file__mutmut_21'] = x__stored_file__mutmut_21 # type: ignore # mutmut generated


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

    # Save the file names
    _ = save_study_unit(
        "/save-file-names",
        {
            "file_metadata": uploaded_files,
            "folder_id": resolved_folder_id,
        },
    )

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
mutants_x__converted_to_pdf__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__converted_to_pdf__mutmut)
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


def x__converted_to_pdf__mutmut_orig(input_path: Path, file_id: str) -> bytes:
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


def x__converted_to_pdf__mutmut_1(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = None

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_2(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            None,
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


def x__converted_to_pdf__mutmut_3(input_path: Path, file_id: str) -> bytes:
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
            capture_output=None,
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


def x__converted_to_pdf__mutmut_4(input_path: Path, file_id: str) -> bytes:
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
            check=None,
            timeout=_CONVERSION_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_5(input_path: Path, file_id: str) -> bytes:
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
            timeout=None,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_6(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
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


def x__converted_to_pdf__mutmut_7(input_path: Path, file_id: str) -> bytes:
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


def x__converted_to_pdf__mutmut_8(input_path: Path, file_id: str) -> bytes:
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
            timeout=_CONVERSION_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_9(input_path: Path, file_id: str) -> bytes:
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
            )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_10(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "XXlibreofficeXX",
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


def x__converted_to_pdf__mutmut_11(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "LIBREOFFICE",
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


def x__converted_to_pdf__mutmut_12(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "XX--headlessXX",
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


def x__converted_to_pdf__mutmut_13(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--HEADLESS",
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


def x__converted_to_pdf__mutmut_14(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "XX--convert-toXX",
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


def x__converted_to_pdf__mutmut_15(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--CONVERT-TO",
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


def x__converted_to_pdf__mutmut_16(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                _PDF_EXTENSION,
                "XX--outdirXX",
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


def x__converted_to_pdf__mutmut_17(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                _PDF_EXTENSION,
                "--OUTDIR",
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


def x__converted_to_pdf__mutmut_18(input_path: Path, file_id: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                _PDF_EXTENSION,
                "--outdir",
                tmp_dir,
                str(None),
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


def x__converted_to_pdf__mutmut_19(input_path: Path, file_id: str) -> bytes:
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
            capture_output=False,
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


def x__converted_to_pdf__mutmut_20(input_path: Path, file_id: str) -> bytes:
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
            check=True,
            timeout=_CONVERSION_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_21(input_path: Path, file_id: str) -> bytes:
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

        if result.returncode == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_22(input_path: Path, file_id: str) -> bytes:
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

        if result.returncode != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_23(input_path: Path, file_id: str) -> bytes:
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
                status_code=None,
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_24(input_path: Path, file_id: str) -> bytes:
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
                detail=None,
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_25(input_path: Path, file_id: str) -> bytes:
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
                detail=f"Conversion failed: {result.stderr.decode()}",
            )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_26(input_path: Path, file_id: str) -> bytes:
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
                )

        pdf_path = Path(tmp_dir) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_27(input_path: Path, file_id: str) -> bytes:
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

        pdf_path = None

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_28(input_path: Path, file_id: str) -> bytes:
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

        pdf_path = Path(tmp_dir) * f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()


def x__converted_to_pdf__mutmut_29(input_path: Path, file_id: str) -> bytes:
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

        pdf_path = Path(None) / f"{file_id}.{_PDF_EXTENSION}"

        return pdf_path.read_bytes()

mutants_x__converted_to_pdf__mutmut['_mutmut_orig'] = x__converted_to_pdf__mutmut_orig # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_1'] = x__converted_to_pdf__mutmut_1 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_2'] = x__converted_to_pdf__mutmut_2 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_3'] = x__converted_to_pdf__mutmut_3 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_4'] = x__converted_to_pdf__mutmut_4 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_5'] = x__converted_to_pdf__mutmut_5 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_6'] = x__converted_to_pdf__mutmut_6 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_7'] = x__converted_to_pdf__mutmut_7 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_8'] = x__converted_to_pdf__mutmut_8 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_9'] = x__converted_to_pdf__mutmut_9 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_10'] = x__converted_to_pdf__mutmut_10 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_11'] = x__converted_to_pdf__mutmut_11 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_12'] = x__converted_to_pdf__mutmut_12 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_13'] = x__converted_to_pdf__mutmut_13 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_14'] = x__converted_to_pdf__mutmut_14 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_15'] = x__converted_to_pdf__mutmut_15 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_16'] = x__converted_to_pdf__mutmut_16 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_17'] = x__converted_to_pdf__mutmut_17 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_18'] = x__converted_to_pdf__mutmut_18 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_19'] = x__converted_to_pdf__mutmut_19 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_20'] = x__converted_to_pdf__mutmut_20 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_21'] = x__converted_to_pdf__mutmut_21 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_22'] = x__converted_to_pdf__mutmut_22 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_23'] = x__converted_to_pdf__mutmut_23 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_24'] = x__converted_to_pdf__mutmut_24 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_25'] = x__converted_to_pdf__mutmut_25 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_26'] = x__converted_to_pdf__mutmut_26 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_27'] = x__converted_to_pdf__mutmut_27 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_28'] = x__converted_to_pdf__mutmut_28 # type: ignore # mutmut generated
mutants_x__converted_to_pdf__mutmut['x__converted_to_pdf__mutmut_29'] = x__converted_to_pdf__mutmut_29 # type: ignore # mutmut generated
