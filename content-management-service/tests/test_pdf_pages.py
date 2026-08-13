import io

import pytest
from pypdf import PdfReader, PdfWriter

from features.study_units_generation.pdf_pages import (
    PageSelectionError,
    PdfPageSelection,
)


def _document(page_count: int) -> bytes:
    writer = PdfWriter()

    for _ in range(page_count):
        _ = writer.add_blank_page(width=200, height=200)

    written = io.BytesIO()
    _ = writer.write(written)

    return written.getvalue()


def _page_count(document: bytes) -> int:
    return len(PdfReader(io.BytesIO(document)).pages)


def test_only_the_asked_pages_survive() -> None:
    selected = PdfPageSelection.sliced(_document(10), 3, 5)

    assert _page_count(selected) == 3


def test_a_single_page_can_be_selected() -> None:
    selected = PdfPageSelection.sliced(_document(10), 7, 7)

    assert _page_count(selected) == 1


def test_an_end_past_the_document_stops_at_the_last_page() -> None:
    selected = PdfPageSelection.sliced(_document(4), 3, 99)

    assert _page_count(selected) == 2


def test_a_start_past_the_document_is_refused() -> None:
    with pytest.raises(PageSelectionError) as refusal:
        _ = PdfPageSelection.sliced(_document(4), 5, 9)

    assert str(refusal.value) == "The document has only 4 pages"


def test_the_final_page_can_be_selected() -> None:
    selected = PdfPageSelection.sliced(_document(4), 4, 4)

    assert _page_count(selected) == 1


def test_no_end_reads_on_to_the_last_page() -> None:
    selected = PdfPageSelection.sliced(_document(10), 8, None)

    assert _page_count(selected) == 3
