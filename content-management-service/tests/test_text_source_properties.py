import tempfile
from pathlib import Path
from unittest import mock

import pytest
import textract
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from features.study_units_generation import link_text, text_sources
from features.study_units_generation.link_text import WebLinkText
from features.study_units_generation.pdf_pages import PageSelectionError
from features.study_units_generation.text_sources import (
    PageRange,
    StoredDocument,
    StoredDocumentText,
    get_file_from_storage,
    provide_stored_document_text,
)
from tests.extraction_support import read_the_document
from tests.pdf_support import PdfDocuments

_PAGES = st.integers(min_value=1, max_value=20)
_STORAGE_NAMES = st.text(alphabet="abcdef0123456789", min_size=3, max_size=8)
_WRITTEN_TEXT = st.text(alphabet="abc \n", max_size=24)
_STORED_DOCUMENT_TEXT = provide_stored_document_text()


def _chunk_for(file_bytes: bytes, document: StoredDocument) -> str:
    _ = file_bytes

    return f"{document.storage_name}|"


@settings(max_examples=50)
@given(_PAGES, _PAGES)
def test_validated_order_property_refuses_a_range_that_runs_backwards(
    first: int, last: int
) -> None:
    if last < first:
        with pytest.raises(ValidationError):
            _ = PageRange(first=first, last=last)

        return

    assert PageRange(first=first, last=last).last == last


@settings(max_examples=25, deadline=None)
@given(_STORAGE_NAMES, st.binary(max_size=32))
def test_get_file_from_storage_property_round_trips_the_stored_bytes(
    storage_name: str, content: bytes
) -> None:
    with tempfile.TemporaryDirectory() as storage:
        _ = (Path(storage) / storage_name).write_bytes(content)

        with mock.patch.object(text_sources, "_FILES_DIRECTORY", storage):
            assert get_file_from_storage(storage_name) == content


@settings(max_examples=25, deadline=None)
@given(st.lists(_STORAGE_NAMES, unique=True, max_size=3))
def test_text_from_files_property_joins_one_chunk_per_file(
    names: list[str],
) -> None:
    documents = [
        StoredDocument(storage_name=name, extension="txt")
        for name in names
    ]

    with (
        mock.patch.object(
            text_sources, "get_file_from_storage", return_value=b""
        ),
        mock.patch.object(
            StoredDocumentText,
            "_text_from_bytes",
            mock.Mock(side_effect=_chunk_for),
        ),
    ):
        joined = _STORED_DOCUMENT_TEXT.text_from_files(documents)

    assert joined == "".join(f"{name}|" for name in names)


@settings(max_examples=25, deadline=None)
@given(st.sampled_from(["txt", "csv", "json", "png"]))
def test__readable_document_property_refuses_pages_from_an_unpaged_file(
    extension: str,
) -> None:
    document = StoredDocument(
        storage_name=f"f.{extension}",
        extension=extension,
        pages=PageRange(first=1),
    )

    with pytest.raises(PageSelectionError):
        _ = _STORED_DOCUMENT_TEXT._readable_document(b"anything", document)


@settings(max_examples=10, deadline=None)
@given(st.integers(min_value=1, max_value=4))
def test__text_from_bytes_property_stays_empty_without_an_extractor(
    page_count: int,
) -> None:
    document = StoredDocument(
        storage_name="f.unheard-of", extension="unheard-of"
    )

    blank_pages = PdfDocuments.blank(page_count)

    assert (
        _STORED_DOCUMENT_TEXT._text_from_bytes(blank_pages, document) == ""
    )


@settings(max_examples=25, deadline=None)
@given(body=st.text(max_size=20), from_youtube=st.booleans())
def test_text_from_link_property_never_answers_with_none(
    *, body: str, from_youtube: bool
) -> None:
    link = (
        "https://www.youtube.com/watch?v=abc"
        if from_youtube
        else "https://example.com/a"
    )

    with (
        mock.patch.object(
            link_text, "get_youtube_transcript_auto", return_value=None
        ),
        mock.patch.object(
            link_text,
            "extract_link_main_content",
            return_value=body or None,
        ),
    ):
        extracted = WebLinkText().text_from_link(link)

    assert extracted == (body or "")


@settings(max_examples=25, deadline=None)
@given(_WRITTEN_TEXT)
def test_provide_stored_document_text_property_reads_back_stored_text(
    written: str,
) -> None:
    document = StoredDocument(storage_name="notes.txt", extension="txt")
    expected = f"{written.strip()}\n" if written.strip() else ""

    with tempfile.TemporaryDirectory() as storage:
        _ = (Path(storage) / document.storage_name).write_text(written)

        with (
            mock.patch.object(text_sources, "_FILES_DIRECTORY", storage),
            mock.patch.object(textract, "process", read_the_document),
        ):
            extracted = provide_stored_document_text().text_from_files(
                [document]
            )

    assert extracted == expected
