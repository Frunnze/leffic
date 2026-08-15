import tempfile
from pathlib import Path
from unittest import mock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from features.study_units_generation import text_sources
from features.study_units_generation.pdf_pages import PageSelectionError
from features.study_units_generation.text_sources import (
    FileMetadata,
    PageRange,
    _readable_document,
    _text_from_bytes,
    get_file_from_storage,
    text_from_files,
    text_from_link,
)
from tests.pdf_support import PdfDocuments

_PAGES = st.integers(min_value=1, max_value=20)
_STORAGE_NAMES = st.text(alphabet="abcdef0123456789", min_size=3, max_size=8)


def _chunk_for(file_bytes: bytes, file_meta: FileMetadata) -> str:
    _ = file_bytes

    return f"{file_meta.file_id}|"


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

        with mock.patch.object(
            text_sources, "_FILES_DIRECTORY", storage
        ):
            assert get_file_from_storage(storage_name) == content


@settings(max_examples=25, deadline=None)
@given(st.lists(_STORAGE_NAMES, unique=True, max_size=3))
def test_text_from_files_property_joins_one_chunk_per_file(
    names: list[str],
) -> None:
    metadata = [
        FileMetadata(file_id=name, extension="txt") for name in names
    ]

    with mock.patch.object(
        text_sources, "get_file_from_storage", return_value=b""
    ):
        with mock.patch.object(
            text_sources, "_text_from_bytes", _chunk_for
        ):
            joined = text_from_files(metadata)

    assert joined == "".join(f"{name}|" for name in names)


@settings(max_examples=25, deadline=None)
@given(st.sampled_from(["txt", "csv", "json", "png"]))
def test__readable_document_property_refuses_pages_from_an_unpaged_file(
    extension: str,
) -> None:
    metadata = FileMetadata(
        file_id="f", extension=extension, pages=PageRange(first=1)
    )

    with pytest.raises(PageSelectionError):
        _ = _readable_document(b"anything", metadata)


@settings(max_examples=10, deadline=None)
@given(st.integers(min_value=1, max_value=4))
def test__text_from_bytes_property_stays_empty_without_an_extractor(
    page_count: int,
) -> None:
    metadata = FileMetadata(file_id="f", extension="unheard-of")

    assert _text_from_bytes(PdfDocuments.blank(page_count), metadata) == ""


@settings(max_examples=25, deadline=None)
@given(st.text(max_size=20), st.booleans())
def test_text_from_link_property_never_answers_with_none(
    body: str, from_youtube: bool
) -> None:
    link = (
        "https://www.youtube.com/watch?v=abc"
        if from_youtube
        else "https://example.com/a"
    )

    with mock.patch.object(
        text_sources, "get_youtube_transcript_auto", return_value=None
    ):
        with mock.patch.object(
            text_sources,
            "extract_link_main_content",
            return_value=body or None,
        ):
            extracted = text_from_link(link)

    assert extracted == (body or "")
