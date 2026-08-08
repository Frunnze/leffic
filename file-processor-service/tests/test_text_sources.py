from pathlib import Path
from unittest import mock

import textract

from features.study_units_generation import text_sources
from features.study_units_generation.text_extractor import (
    GeneralTextExtractor,
    TextExtractorFactory,
    text_extractor_factory,
)
from features.study_units_generation.text_sources import (
    FileMetadata,
    get_file_from_storage,
    text_from_files,
    text_from_link,
)

_FILE_ID = "3f6c2b1a"
_PDF = FileMetadata(file_id=_FILE_ID, extension="pdf")


def test_the_factory_knows_the_registered_extensions() -> None:
    assert isinstance(
        text_extractor_factory.get_text_extractor("pdf"), GeneralTextExtractor
    )


def test_the_factory_is_case_insensitive() -> None:
    assert text_extractor_factory.get_text_extractor("PDF") is not None


def test_the_factory_returns_nothing_for_an_unknown_extension() -> None:
    assert text_extractor_factory.get_text_extractor("xyz") is None


def test_a_registered_extractor_is_returned() -> None:
    factory = TextExtractorFactory()
    extractor = GeneralTextExtractor()
    factory.register_extractor("md", extractor)

    assert factory.get_text_extractor("md") is extractor


def test_the_extractor_decodes_and_strips_the_document() -> None:
    with mock.patch.object(
        textract, "process", return_value=b"  hello world  "
    ):
        text = GeneralTextExtractor().extract_text("f.pdf", "pdf")

    assert text == "hello world"


def test_reads_a_stored_file(tmp_path: Path) -> None:
    stored = tmp_path / "stored.bin"
    _ = stored.write_bytes(b"payload")

    with mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)):
        assert get_file_from_storage("stored.bin") == b"payload"


def test_text_from_files_joins_every_document(tmp_path: Path) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(b"payload")

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(
            text_sources, "_TEMPORARY_DIRECTORY", str(tmp_path)
        ),
        mock.patch.object(textract, "process", return_value=b"page one"),
    ):
        assert text_from_files([_PDF]) == "page one\n"


def test_text_from_files_skips_unknown_extensions(tmp_path: Path) -> None:
    unknown = FileMetadata(file_id=_FILE_ID, extension="xyz")
    _ = (tmp_path / f"{_FILE_ID}.xyz").write_bytes(b"payload")

    with mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)):
        assert text_from_files([unknown]) == ""


def test_text_from_files_skips_documents_with_no_text(
    tmp_path: Path,
) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(b"payload")

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(
            text_sources, "_TEMPORARY_DIRECTORY", str(tmp_path)
        ),
        mock.patch.object(textract, "process", return_value=b"   "),
    ):
        assert text_from_files([_PDF]) == ""


def test_a_youtube_link_uses_the_transcript() -> None:
    with mock.patch.object(
        text_sources, "get_youtube_transcript_auto", return_value="spoken"
    ):
        assert text_from_link("https://youtube.com/watch?v=x") == "spoken"


def test_a_youtube_link_without_a_transcript_reads_the_page() -> None:
    with (
        mock.patch.object(
            text_sources, "get_youtube_transcript_auto", return_value=None
        ),
        mock.patch.object(
            text_sources, "extract_link_main_content", return_value="page"
        ),
    ):
        assert text_from_link("https://youtube.com/watch?v=x") == "page"


def test_a_plain_link_reads_the_page() -> None:
    with mock.patch.object(
        text_sources, "extract_link_main_content", return_value="article"
    ):
        assert text_from_link("https://example.com") == "article"


def test_an_unreadable_link_yields_no_text() -> None:
    with mock.patch.object(
        text_sources, "extract_link_main_content", return_value=None
    ):
        assert text_from_link("https://example.com") == ""
