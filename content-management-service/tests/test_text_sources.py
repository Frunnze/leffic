import tempfile
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
)

_FILE_ID = "3f6c2b1a"
_OTHER_FILE_ID = "9a1d4c7b"
_PDF = FileMetadata(file_id=_FILE_ID, extension="pdf")


def _read_the_document(filename: str, **_: object) -> bytes:
    return Path(filename).read_bytes()


class RecordingExtractor:
    def __init__(self, seen: list[str], extensions: list[str]) -> None:
        super().__init__()
        self.seen: list[str] = seen
        self.extensions: list[str] = extensions

    def __call__(
        self, filename: str, extension: str = "", **_: object
    ) -> bytes:
        self.seen.append(filename)
        self.extensions.append(extension)

        return Path(filename).read_bytes()


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
    other = FileMetadata(file_id=_OTHER_FILE_ID, extension="pdf")
    _ = (tmp_path / f"{_OTHER_FILE_ID}.pdf").write_bytes(b"second")

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(textract, "process", _read_the_document),
    ):
        joined = text_from_files([_PDF, other])

    assert joined == "payload\nsecond\n"


def test_the_document_is_written_where_the_extractor_can_read_it(
    tmp_path: Path,
) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(b"payload")
    seen: list[str] = []
    extensions: list[str] = []

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(
            textract, "process", RecordingExtractor(seen, extensions)
        ),
    ):
        _ = text_from_files([_PDF])

    assert seen[0].startswith(tempfile.gettempdir())
    assert seen[0].endswith(_FILE_ID)
    assert not Path(seen[0]).exists()
    assert extensions == ["pdf"]


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
        mock.patch.object(textract, "process", return_value=b"   "),
    ):
        assert text_from_files([_PDF]) == ""


def test_extraction_needs_no_pre_created_directory(tmp_path: Path) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(b"payload")

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(textract, "process", _read_the_document),
    ):
        extracted = text_from_files([_PDF])

    assert extracted == "payload\n"
