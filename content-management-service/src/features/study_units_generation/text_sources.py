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

_FILES_DIRECTORY = "files"
_YOUTUBE_HOST = "youtube.com"
_PDF_EXTENSION = "pdf"
_NOT_A_PDF = "Only a PDF can be read by page"
_BACKWARDS_RANGE = "The last page comes before the first"


class PageRange(BaseModel):
    first: int = Field(ge=1)
    last: int = Field(ge=1)

    @model_validator(mode="after")
    def validated_order(self) -> "PageRange":
        if self.last < self.first:
            raise ValueError(_BACKWARDS_RANGE)

        return self


class FileMetadata(BaseModel):
    file_id: str
    extension: str
    pages: PageRange | None = None


def get_file_from_storage(storage_name: str) -> bytes:
    return (Path(_FILES_DIRECTORY) / storage_name).read_bytes()


def text_from_files(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def _asked_pages(file_bytes: bytes, file_meta: FileMetadata) -> bytes:
    asked = file_meta.pages

    if asked is None:
        return file_bytes

    if file_meta.extension.lower() != _PDF_EXTENSION:
        raise PageSelectionError(_NOT_A_PDF)

    return PdfPageSelection.sliced(file_bytes, asked.first, asked.last)


def _text_from_bytes(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id
    ) as temp_file:
        _ = temp_file.write(_asked_pages(file_bytes, file_meta))
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def text_from_link(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""
