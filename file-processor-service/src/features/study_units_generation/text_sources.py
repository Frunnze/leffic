import tempfile
from pathlib import Path

from pydantic import BaseModel

from src.features.study_units_generation.link_extractor import (
    extract_link_main_content,
    get_youtube_transcript_auto,
)
from src.features.study_units_generation.text_extractor import (
    text_extractor_factory,
)

_FILES_DIRECTORY = "files"
_TEMPORARY_DIRECTORY = "temp_files"
_YOUTUBE_HOST = "youtube.com"


class FileMetadata(BaseModel):
    file_id: str
    extension: str


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


def _text_from_bytes(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, delete=True, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def text_from_link(link: str) -> str:
    extracted_text = ""

    if _YOUTUBE_HOST in link:
        extracted_text = get_youtube_transcript_auto(link)

    if not extracted_text:
        extracted_text = extract_link_main_content(link)

    return extracted_text or ""
