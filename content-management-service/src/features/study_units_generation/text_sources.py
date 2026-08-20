import tempfile
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from features.study_units_generation.link_extractor import (
    extract_link_main_content,
    get_youtube_transcript_auto,
)
from features.study_units_generation.pdf_pages import (
    PageSelectionError,
    PdfPageSelection,
)
from features.study_units_generation.text_extractor import (
    text_extractor_factory,
)
from shared.pdf_conversion import PdfConversion

_FILES_DIRECTORY = "files"
_YOUTUBE_HOST = "youtube.com"
_PDF_EXTENSION = "pdf"
_PAGED_EXTENSIONS = (
    "pdf", "doc", "docx", "odt", "rtf", "ppt", "pptx", "odp",
)
_NOT_PAGED = "Only a document with pages can be read"
_BACKWARDS_RANGE = "The last page comes before the first"
_MISSING_DOCUMENT = "That document is no longer stored"


class PageRange(BaseModel):
    first: int = Field(default=1, ge=1)
    last: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validated_order(self) -> "PageRange":
        if self.last is not None and self.last < self.first:
            raise ValueError(_BACKWARDS_RANGE)

        return self


class FileMetadata(BaseModel):
    file_id: str
    extension: str
    pages: PageRange | None = None


class MissingDocumentError(Exception):
    def __init__(self) -> None:
        super().__init__(_MISSING_DOCUMENT)


def get_file_from_storage(storage_name: str) -> bytes:
    stored = Path(_FILES_DIRECTORY) / storage_name

    try:
        return stored.read_bytes()
    except OSError as unreadable:
        raise MissingDocumentError from unreadable


def text_from_files(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def _readable_document(
    file_bytes: bytes, file_meta: FileMetadata
) -> tuple[bytes, str]:
    asked = file_meta.pages
    extension = file_meta.extension.lower()

    if asked is None:
        return file_bytes, file_meta.extension

    if extension not in _PAGED_EXTENSIONS:
        raise PageSelectionError(_NOT_PAGED)

    if extension == _PDF_EXTENSION:
        paginated = file_bytes
    else:
        paginated = PdfConversion.converted(file_bytes, extension)

    sliced = PdfPageSelection.sliced(paginated, asked.first, asked.last)

    return sliced, _PDF_EXTENSION


def _text_from_bytes(file_bytes: bytes, file_meta: FileMetadata) -> str:
    document, extension = _readable_document(file_bytes, file_meta)
    text_extractor = text_extractor_factory.get_text_extractor(extension)

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id
    ) as temp_file:
        _ = temp_file.write(document)
        temp_file.flush()
        extracted = text_extractor.extract_text(temp_file.name, extension)

    return f"{extracted}\n" if extracted else ""


def text_from_link(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""
