import subprocess
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, cast
from unittest import mock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.pdf_pages import (
    PageSelectionError,
    PdfPageSelection,
)
from shared.models.columns import FlexibleUuid
from shared.pdf_conversion import ConversionError, PdfConversion
from tests.pdf_support import LibreOfficeStub, PdfDocuments

if TYPE_CHECKING:
    from sqlalchemy import Dialect

_EXTENSIONS = st.sampled_from(["docx", "odt", "pptx", "rtf"])
_PAGE_COUNTS = st.integers(min_value=1, max_value=6)
_SUBPROCESS_RUN = "shared.pdf_conversion.subprocess.run"


@settings(max_examples=50)
@given(st.uuids())
def test_process_bind_param_property_reads_a_uuid_in_any_spelling(
    identifier: uuid.UUID,
) -> None:
    column = FlexibleUuid()

    dialect = cast("Dialect", cast("object", None))

    assert column.process_bind_param(identifier, dialect) == identifier
    assert (
        column.process_bind_param(str(identifier), dialect) == identifier
    )
    assert column.process_bind_param(None, dialect) is None


@settings(max_examples=50)
@given(_EXTENSIONS, st.text(alphabet="abc", min_size=1, max_size=6))
def test__command_property_always_writes_a_pdf_into_the_given_directory(
    extension: str, directory: str
) -> None:
    source = Path(f"/work/document.{extension}")
    command = PdfConversion._command(source, directory)

    assert command[0] == "libreoffice"
    assert "--headless" in command
    assert command[command.index("--convert-to") + 1] == "pdf"
    assert command[command.index("--outdir") + 1] == directory
    assert command[-1] == str(source)


@settings(max_examples=10, deadline=None)
@given(_EXTENSIONS, _PAGE_COUNTS)
def test_converted_property_hands_back_a_pdf_of_the_written_pages(
    extension: str, page_count: int
) -> None:
    stub = LibreOfficeStub(page_count)

    with mock.patch(_SUBPROCESS_RUN, stub):
        produced = PdfConversion.converted(b"anything", extension)

    assert PdfDocuments.page_count(produced) == page_count
    assert stub.converted_sources == [f"document.{extension}"]


@settings(max_examples=10, deadline=None)
@given(st.integers(min_value=1, max_value=9))
def test__written_pdf_property_reports_whatever_libreoffice_complained(
    return_code: int,
) -> None:
    failure = subprocess.CompletedProcess(
        args=[], returncode=return_code, stderr=b"it went wrong"
    )

    with (
        mock.patch(_SUBPROCESS_RUN, return_value=failure),
        pytest.raises(ConversionError, match="it went wrong"),
    ):
        _ = PdfConversion.converted(b"anything", "docx")


@settings(max_examples=25, deadline=None)
@given(_PAGE_COUNTS, st.integers(min_value=1, max_value=6))
def test_sliced_property_keeps_exactly_the_pages_that_were_asked_for(
    page_count: int, first_page: int
) -> None:
    document = PdfDocuments.blank(page_count)

    if first_page > page_count:
        with pytest.raises(PageSelectionError):
            _ = PdfPageSelection.sliced(document, first_page, None)

        return

    selected = PdfPageSelection.sliced(document, first_page, page_count)

    assert PdfDocuments.page_count(selected) == page_count - first_page + 1
