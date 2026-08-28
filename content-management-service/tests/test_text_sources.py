import inspect
import tempfile
from pathlib import Path
from unittest import mock

import textract

from features.study_units_generation import (
    extraction_router,
    text_sources,
)
from features.study_units_generation.text_extractor import (
    GeneralTextExtractor,
    TextExtractorFactory,
    text_extractor_factory,
)
from features.study_units_generation.text_sources import (
    StoredDocument,
    get_file_from_storage,
    text_from_files,
)
from tests.extraction_support import read_the_document

_FILE_ID = "3f6c2b1a"
_OTHER_FILE_ID = "9a1d4c7b"
_PDF = StoredDocument(storage_name=f"{_FILE_ID}.pdf", extension="pdf")
_STORAGE_CONSTANT = '_FILES_DIRECTORY = "files"'


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


def test_text_from_files_reads_the_given_storage_name() -> None:
    document = StoredDocument(
        storage_name="a-name-nobody-would-build", extension="pdf"
    )

    with (
        mock.patch.object(
            text_sources, "get_file_from_storage", return_value=b""
        ) as reader,
        mock.patch.object(textract, "process", read_the_document),
    ):
        _ = text_from_files([document])

    assert reader.call_args.args[0] == "a-name-nobody-would-build"


def test_text_sources_has_no_database_import() -> None:
    source = inspect.getsource(text_sources)

    assert "sqlalchemy" not in source
    assert "shared.models" not in source


def test_reads_stay_in_one_place() -> None:
    router_source = inspect.getsource(extraction_router)

    assert "Path(" not in router_source
    assert "_FILES_DIRECTORY" not in router_source
    assert inspect.getsource(text_sources).count(_STORAGE_CONSTANT) == 1


def test_text_from_files_joins_every_document(tmp_path: Path) -> None:
    _ = (tmp_path / f"{_FILE_ID}.pdf").write_bytes(b"payload")
    other = StoredDocument(
        storage_name=f"{_OTHER_FILE_ID}.pdf", extension="pdf"
    )
    _ = (tmp_path / f"{_OTHER_FILE_ID}.pdf").write_bytes(b"second")

    with (
        mock.patch.object(text_sources, "_FILES_DIRECTORY", str(tmp_path)),
        mock.patch.object(textract, "process", read_the_document),
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
    assert seen[0].endswith(_PDF.storage_name)
    assert not Path(seen[0]).exists()
    assert extensions == ["pdf"]


def test_text_from_files_skips_unknown_extensions(tmp_path: Path) -> None:
    unknown = StoredDocument(
        storage_name=f"{_FILE_ID}.xyz", extension="xyz"
    )
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
        mock.patch.object(textract, "process", read_the_document),
    ):
        extracted = text_from_files([_PDF])

    assert extracted == "payload\n"
