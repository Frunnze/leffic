import subprocess
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
import textract

from features.study_units_generation import text_sources
from features.study_units_generation.text_sources import (
    PageRange,
    StoredDocument,
    text_from_files,
)
from tests.pdf_support import (
    DocumentRecorder,
    LibreOfficeStub,
    PdfDocuments,
)

_FILE_ID = "3f6c2b1a"


def _extraction_of_a_ranged_docx(
    tmp_path: Path, libreoffice: LibreOfficeStub
) -> DocumentRecorder:
    _ = (tmp_path / f"{_FILE_ID}.docx").write_bytes(b"docx payload")
    ranged = StoredDocument(
        storage_name=f"{_FILE_ID}.docx",
        extension="docx",
        pages=PageRange(first=2, last=3),
    )
    recorder = DocumentRecorder([])

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(subprocess, "run", libreoffice),
        mock.patch.object(textract, "process", recorder),
    ):
        _ = text_from_files([ranged])

    return recorder


def test_a_page_range_on_a_docx_slices_the_converted_pdf(
    tmp_path: Path,
) -> None:
    recorder = _extraction_of_a_ranged_docx(tmp_path, LibreOfficeStub(6))
    expected_page_count = 2

    assert (
        PdfDocuments.page_count(recorder.documents[0]) == expected_page_count
    )


def test_a_sliced_docx_is_extracted_as_a_pdf(tmp_path: Path) -> None:
    recorder = _extraction_of_a_ranged_docx(tmp_path, LibreOfficeStub(6))

    assert recorder.extensions[0] == "pdf"


def test_the_docx_itself_is_what_libreoffice_converts(
    tmp_path: Path,
) -> None:
    libreoffice = LibreOfficeStub(6)

    _ = _extraction_of_a_ranged_docx(tmp_path, libreoffice)

    assert libreoffice.converted_sources == ["document.docx"]


def test_a_docx_without_a_page_range_is_never_converted(
    tmp_path: Path,
) -> None:
    _ = (tmp_path / f"{_FILE_ID}.docx").write_bytes(b"docx payload")
    whole = StoredDocument(
        storage_name=f"{_FILE_ID}.docx", extension="docx"
    )
    libreoffice = LibreOfficeStub(6)
    recorder = DocumentRecorder([])

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(subprocess, "run", libreoffice),
        mock.patch.object(textract, "process", recorder),
    ):
        _ = text_from_files([whole])

    assert libreoffice.converted_sources == []
    assert recorder.extensions == ["docx"]


@pytest.mark.parametrize(
    "extension",
    ["pdf", "doc", "docx", "odt", "rtf", "ppt", "pptx", "odp"],
)
def test_every_paged_format_accepts_a_range(
    tmp_path: Path, extension: str
) -> None:
    stored = tmp_path / f"{_FILE_ID}.{extension}"
    _ = stored.write_bytes(PdfDocuments.blank(6))
    ranged = StoredDocument(
        storage_name=f"{_FILE_ID}.{extension}",
        extension=extension,
        pages=PageRange(first=1, last=2),
    )
    recorder = DocumentRecorder([])
    expected_page_count = 2

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(subprocess, "run", LibreOfficeStub(6)),
        mock.patch.object(textract, "process", recorder),
    ):
        _ = text_from_files([ranged])

    assert (
        PdfDocuments.page_count(recorder.documents[0]) == expected_page_count
    )


def test_temporary_file_is_suffixed_with_the_storage_name(
    tmp_path: Path,
) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(PdfDocuments.blank(2))
    document = StoredDocument(
        storage_name=f"{_FILE_ID}.pdf", extension="pdf"
    )
    extractor = mock.Mock(return_value=b"")

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(textract, "process", extractor),
    ):
        _ = text_from_files([document])

    written = cast("str", extractor.call_args.args[0])

    assert written.endswith(document.storage_name)
