import tempfile
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.pdf_pages import (
    PageSelectionError,
    PdfPageSelection,
)
from shared.models.columns import FlexibleUuid
from shared.pdf_conversion import ConversionError, PdfConversion
from tests.pdf_support import CopyingExporter, PdfDocuments, SilentExporter

if TYPE_CHECKING:
    from sqlalchemy import Dialect

_EXTENSIONS = st.sampled_from(["docx", "odt", "pptx", "rtf"])
_PAGE_COUNTS = st.integers(min_value=1, max_value=6)
_DOCUMENTS = st.binary(max_size=64)
_NO_OUTPUT = "LibreOffice produced no PDF"


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


@settings(max_examples=25, deadline=None)
@given(_EXTENSIONS, _DOCUMENTS)
def test_converted_property_hands_back_exactly_what_was_exported(
    extension: str, document: bytes
) -> None:
    conversion = PdfConversion(CopyingExporter())

    assert conversion.converted(document, extension) == document


@settings(max_examples=25, deadline=None)
@given(_EXTENSIONS, _DOCUMENTS)
def test_converted_property_refuses_when_no_pdf_was_exported(
    extension: str, document: bytes
) -> None:
    conversion = PdfConversion(SilentExporter())

    with pytest.raises(ConversionError, match=_NO_OUTPUT):
        _ = conversion.converted(document, extension)


@settings(max_examples=25, deadline=None)
@given(_EXTENSIONS, _DOCUMENTS)
def test_converted_file_property_converts_the_stored_bytes(
    extension: str, document: bytes
) -> None:
    conversion = PdfConversion(CopyingExporter())

    with tempfile.TemporaryDirectory() as storage:
        stored = Path(storage) / f"stored.{extension}"
        _ = stored.write_bytes(document)

        converted = conversion.converted_file(stored, extension)

    assert converted == conversion.converted(document, extension)


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
