import io
import tempfile
import uuid
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi import HTTPException, UploadFile
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.file_upload import file_uploader as uploader_module
from features.file_upload.file_uploader import (
    _converted_to_pdf,
    _recorded_files,
    _stored_file,
    save_file_to_storage,
)
from shared.models import File as StoredFile
from shared.pdf_conversion import ConversionError
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_BAD_REQUEST = 400
_CLIENT, _SESSIONS = property_world()
_EXTENSIONS = st.sampled_from(["pdf", "docx", "txt", "png"])
_CONTENT = st.binary(min_size=1, max_size=32)
_STORAGE = tempfile.mkdtemp()
_PDF_CONVERTED = (
    "features.file_upload.file_uploader.PdfConversion.converted"
)


def _stored_names(session: Session, folder_id: uuid.UUID) -> list[str]:
    rows = (
        session.query(StoredFile)
        .filter(StoredFile.folder_id == folder_id)
        .all()
    )

    return [row.name for row in rows]


def _written_document() -> Path:
    written = Path(_STORAGE) / "document.docx"
    _ = written.write_bytes(b"body")

    return written


def _upload(name: str, content: bytes) -> UploadFile:
    return UploadFile(filename=name, file=io.BytesIO(content))


@settings(max_examples=25, deadline=None)
@given(_EXTENSIONS, _CONTENT)
def test_save_file_to_storage_property_writes_exactly_what_was_uploaded(
    extension: str, content: bytes
) -> None:
    unique_name = f"{uuid.uuid4()}.{extension}"

    with mock.patch.object(
        uploader_module, "_FILES_DIRECTORY", _STORAGE
    ) as storage:
        save_file_to_storage(_upload(f"a.{extension}", content), unique_name)

        assert (Path(storage) / unique_name).read_bytes() == content


@settings(max_examples=25, deadline=None)
@given(_EXTENSIONS, _CONTENT)
def test__stored_file_property_describes_the_upload_it_just_wrote(
    extension: str, content: bytes
) -> None:
    with mock.patch.object(
        uploader_module, "_FILES_DIRECTORY", _STORAGE
    ):
        described = _stored_file(_upload(f"notes.{extension}", content))

    assert described["extension"] == extension
    assert described["name"] == f"notes.{extension}"
    assert uuid.UUID(described["file_id"])


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.integers(min_value=1, max_value=3))
def test__recorded_files_property_files_every_upload_under_the_folder(
    owner: uuid.UUID, file_count: int
) -> None:
    uploaded = [
        {
            "file_id": str(uuid.uuid4()),
            "extension": "pdf",
            "name": f"notes-{index}.pdf",
        }
        for index in range(file_count)
    ]

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        _recorded_files(session, str(folder_id), uploaded)
        stored = _stored_names(session, folder_id)

    assert sorted(stored) == sorted(item["name"] for item in uploaded)


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__recorded_files_property_refuses_a_folder_that_is_not_there(
    absent: uuid.UUID,
) -> None:
    with _SESSIONS() as session, pytest.raises(HTTPException) as raised:
        _recorded_files(session, str(absent), [])

    assert raised.value.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _EXTENSIONS)
def test_upload_files_property_answers_with_one_entry_per_file(
    owner: uuid.UUID, extension: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

    with mock.patch.object(
        uploader_module, "_FILES_DIRECTORY", _STORAGE
    ):
        response = _CLIENT.post(
            "/upload-files",
            files=[("files", (f"a.{extension}", b"body"))],
            data={"folder_id": str(folder_id)},
            headers=authorization(str(owner)),
        )

    body = cast("dict[str, object]", response.json())
    described = cast("list[object]", body["file_metadata"])

    assert response.status_code == _OK
    assert len(described) == 1


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _EXTENSIONS)
def test_get_file_property_reports_a_file_that_is_not_stored(
    file_id: uuid.UUID, extension: str
) -> None:
    with mock.patch.object(
        uploader_module, "_FILES_DIRECTORY", _STORAGE
    ):
        response = _CLIENT.get(
            "/file",
            params={
                "file_id": str(file_id),
                "file_extension": extension,
            },
        )

    assert response.status_code == _NOT_FOUND


@settings(max_examples=10, deadline=None)
@given(st.sampled_from(["docx", "odt", "rtf"]))
def test__converted_to_pdf_property_translates_a_refusal_into_a_bad_request(
    extension: str,
) -> None:
    with mock.patch(
        _PDF_CONVERTED, side_effect=ConversionError("no good")
    ), pytest.raises(HTTPException) as raised:
        _ = _converted_to_pdf(_written_document(), extension)

    assert raised.value.status_code == _BAD_REQUEST
