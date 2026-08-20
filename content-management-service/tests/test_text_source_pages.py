from pathlib import Path
from unittest import mock

import pytest
import textract
from pydantic import ValidationError

from features.study_units_generation import text_sources
from features.study_units_generation.pdf_pages import PageSelectionError
from features.study_units_generation.text_sources import (
    FileMetadata,
    PageRange,
    text_from_files,
)
from tests.pdf_support import DocumentRecorder, PdfDocuments

_FILE_ID = "3f6c2b1a"


def _pages_reaching_the_extractor(tmp_path: Path, asked: PageRange) -> int:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(PdfDocuments.blank(6))
    ranged = FileMetadata(file_id=_FILE_ID, extension="pdf", pages=asked)
    recorder = DocumentRecorder([])

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(textract, "process", recorder),
    ):
        _ = text_from_files([ranged])

    return PdfDocuments.page_count(recorder.documents[0])


def test_only_the_asked_pages_reach_the_extractor(tmp_path: Path) -> None:
    asked = PageRange(first=2, last=3)
    expected_page_count = 2

    assert _pages_reaching_the_extractor(tmp_path, asked) == (
        expected_page_count
    )


def test_only_an_end_page_reads_from_the_first_page(tmp_path: Path) -> None:
    asked = PageRange(last=2)
    expected_page_count = 2

    assert _pages_reaching_the_extractor(tmp_path, asked) == (
        expected_page_count
    )


def test_only_a_start_page_reads_on_to_the_end(tmp_path: Path) -> None:
    asked = PageRange(first=5)
    expected_page_count = 2

    assert _pages_reaching_the_extractor(tmp_path, asked) == (
        expected_page_count
    )


def test_a_backwards_range_is_refused() -> None:
    with pytest.raises(ValidationError):
        _ = PageRange(first=8, last=3)


def test_a_page_range_on_a_document_without_pages_is_refused(
    tmp_path: Path,
) -> None:
    _ = (tmp_path / f"{_FILE_ID}.txt").write_bytes(b"payload")
    ranged = FileMetadata(
        file_id=_FILE_ID,
        extension="txt",
        pages=PageRange(first=1, last=2),
    )

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        pytest.raises(PageSelectionError) as refusal,
    ):
        _ = text_from_files([ranged])

    assert str(refusal.value) == "Only a document with pages can be read"
