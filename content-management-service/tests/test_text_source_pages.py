import io
from pathlib import Path
from unittest import mock

import pytest
import textract
from pypdf import PdfReader, PdfWriter

from features.study_units_generation import text_sources
from features.study_units_generation.pdf_pages import PageSelectionError
from features.study_units_generation.text_sources import (
    FileMetadata,
    PageRange,
    text_from_files,
)

_FILE_ID = "3f6c2b1a"


class DocumentRecorder:
    def __init__(self, documents: list[bytes]) -> None:
        super().__init__()
        self.documents: list[bytes] = documents

    def __call__(
        self, filename: str, extension: str = "", **_unused: object
    ) -> bytes:
        _ = extension
        self.documents.append(Path(filename).read_bytes())

        return b""


def _pdf_document(page_count: int) -> bytes:
    writer = PdfWriter()

    for _ in range(page_count):
        _ = writer.add_blank_page(width=200, height=200)

    written = io.BytesIO()
    _ = writer.write(written)

    return written.getvalue()


def _pdf_page_count(document: bytes) -> int:
    return len(PdfReader(io.BytesIO(document)).pages)


def test_only_the_asked_pages_reach_the_extractor(tmp_path: Path) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(_pdf_document(6))
    ranged = FileMetadata(
        file_id=_FILE_ID,
        extension="pdf",
        pages=PageRange(first=2, last=3),
    )
    extracted_documents: list[bytes] = []

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(
            textract, "process", DocumentRecorder(extracted_documents)
        ),
    ):
        _ = text_from_files([ranged])

    assert _pdf_page_count(extracted_documents[0]) == 2


def test_a_page_range_on_a_document_that_is_not_a_pdf_is_refused(
    tmp_path: Path,
) -> None:
    _ = (tmp_path / f"{_FILE_ID}.docx").write_bytes(b"payload")
    ranged = FileMetadata(
        file_id=_FILE_ID,
        extension="docx",
        pages=PageRange(first=1, last=2),
    )

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        pytest.raises(PageSelectionError) as refusal,
    ):
        _ = text_from_files([ranged])

    assert str(refusal.value) == "Only a PDF can be read by page"
