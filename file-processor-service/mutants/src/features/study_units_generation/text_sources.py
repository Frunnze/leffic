import tempfile
from pathlib import Path

from pydantic import BaseModel

from features.study_units_generation.link_extractor import (
    extract_link_main_content,
    get_youtube_transcript_auto,
)
from features.study_units_generation.text_extractor import (
    text_extractor_factory,
)

_FILES_DIRECTORY = "files"
_TEMPORARY_DIRECTORY = "temp_files"
_YOUTUBE_HOST = "youtube.com"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


class FileMetadata(BaseModel):
    file_id: str
    extension: str
mutants_x_get_file_from_storage__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_file_from_storage__mutmut)
def get_file_from_storage(storage_name: str) -> bytes:
    return (Path(_FILES_DIRECTORY) / storage_name).read_bytes()


def x_get_file_from_storage__mutmut_orig(storage_name: str) -> bytes:
    return (Path(_FILES_DIRECTORY) / storage_name).read_bytes()


def x_get_file_from_storage__mutmut_1(storage_name: str) -> bytes:
    return (Path(_FILES_DIRECTORY) * storage_name).read_bytes()


def x_get_file_from_storage__mutmut_2(storage_name: str) -> bytes:
    return (Path(None) / storage_name).read_bytes()

mutants_x_get_file_from_storage__mutmut['_mutmut_orig'] = x_get_file_from_storage__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_file_from_storage__mutmut['x_get_file_from_storage__mutmut_1'] = x_get_file_from_storage__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_file_from_storage__mutmut['x_get_file_from_storage__mutmut_2'] = x_get_file_from_storage__mutmut_2 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_text_from_files__mutmut)
def text_from_files(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_orig(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_1(file_metadata: list[FileMetadata]) -> str:
    extracted_text = None

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_2(file_metadata: list[FileMetadata]) -> str:
    extracted_text = "XXXX"

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_3(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = None
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_4(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            None
        )
        extracted_text += _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_5(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text = _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_6(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text -= _text_from_bytes(file_bytes, file_meta)

    return extracted_text


def x_text_from_files__mutmut_7(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(None, file_meta)

    return extracted_text


def x_text_from_files__mutmut_8(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, None)

    return extracted_text


def x_text_from_files__mutmut_9(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_meta)

    return extracted_text


def x_text_from_files__mutmut_10(file_metadata: list[FileMetadata]) -> str:
    extracted_text = ""

    for file_meta in file_metadata:
        file_bytes = get_file_from_storage(
            f"{file_meta.file_id}.{file_meta.extension}"
        )
        extracted_text += _text_from_bytes(file_bytes, )

    return extracted_text

mutants_x_text_from_files__mutmut['_mutmut_orig'] = x_text_from_files__mutmut_orig # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_1'] = x_text_from_files__mutmut_1 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_2'] = x_text_from_files__mutmut_2 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_3'] = x_text_from_files__mutmut_3 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_4'] = x_text_from_files__mutmut_4 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_5'] = x_text_from_files__mutmut_5 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_6'] = x_text_from_files__mutmut_6 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_7'] = x_text_from_files__mutmut_7 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_8'] = x_text_from_files__mutmut_8 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_9'] = x_text_from_files__mutmut_9 # type: ignore # mutmut generated
mutants_x_text_from_files__mutmut['x_text_from_files__mutmut_10'] = x_text_from_files__mutmut_10 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__text_from_bytes__mutmut)
def _text_from_bytes(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_orig(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_1(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = None

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_2(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        None
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_3(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is not None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_4(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return "XXXX"

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_5(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=None, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_6(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=None
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_7(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_8(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_9(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = None
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_10(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(None)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_11(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = None

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_12(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            None, file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_13(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, None
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_14(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            file_meta.extension
        )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_15(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, )

    return f"{extracted}\n" if extracted else ""


def x__text_from_bytes__mutmut_16(file_bytes: bytes, file_meta: FileMetadata) -> str:
    text_extractor = text_extractor_factory.get_text_extractor(
        file_meta.extension
    )

    if text_extractor is None:
        return ""

    with tempfile.NamedTemporaryFile(
        suffix=file_meta.file_id, dir=_TEMPORARY_DIRECTORY
    ) as temp_file:
        _ = temp_file.write(file_bytes)
        temp_file.flush()
        extracted = text_extractor.extract_text(
            temp_file.name, file_meta.extension
        )

    return f"{extracted}\n" if extracted else "XXXX"

mutants_x__text_from_bytes__mutmut['_mutmut_orig'] = x__text_from_bytes__mutmut_orig # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_1'] = x__text_from_bytes__mutmut_1 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_2'] = x__text_from_bytes__mutmut_2 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_3'] = x__text_from_bytes__mutmut_3 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_4'] = x__text_from_bytes__mutmut_4 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_5'] = x__text_from_bytes__mutmut_5 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_6'] = x__text_from_bytes__mutmut_6 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_7'] = x__text_from_bytes__mutmut_7 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_8'] = x__text_from_bytes__mutmut_8 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_9'] = x__text_from_bytes__mutmut_9 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_10'] = x__text_from_bytes__mutmut_10 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_11'] = x__text_from_bytes__mutmut_11 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_12'] = x__text_from_bytes__mutmut_12 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_13'] = x__text_from_bytes__mutmut_13 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_14'] = x__text_from_bytes__mutmut_14 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_15'] = x__text_from_bytes__mutmut_15 # type: ignore # mutmut generated
mutants_x__text_from_bytes__mutmut['x__text_from_bytes__mutmut_16'] = x__text_from_bytes__mutmut_16 # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_text_from_link__mutmut)
def text_from_link(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""


def x_text_from_link__mutmut_orig(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""


def x_text_from_link__mutmut_1(link: str) -> str:
    if _YOUTUBE_HOST not in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""


def x_text_from_link__mutmut_2(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = None

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""


def x_text_from_link__mutmut_3(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(None)

        if transcript:
            return transcript

    return extract_link_main_content(link) or ""


def x_text_from_link__mutmut_4(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) and ""


def x_text_from_link__mutmut_5(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(None) or ""


def x_text_from_link__mutmut_6(link: str) -> str:
    if _YOUTUBE_HOST in link:
        transcript = get_youtube_transcript_auto(link)

        if transcript:
            return transcript

    return extract_link_main_content(link) or "XXXX"

mutants_x_text_from_link__mutmut['_mutmut_orig'] = x_text_from_link__mutmut_orig # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut['x_text_from_link__mutmut_1'] = x_text_from_link__mutmut_1 # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut['x_text_from_link__mutmut_2'] = x_text_from_link__mutmut_2 # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut['x_text_from_link__mutmut_3'] = x_text_from_link__mutmut_3 # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut['x_text_from_link__mutmut_4'] = x_text_from_link__mutmut_4 # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut['x_text_from_link__mutmut_5'] = x_text_from_link__mutmut_5 # type: ignore # mutmut generated
mutants_x_text_from_link__mutmut['x_text_from_link__mutmut_6'] = x_text_from_link__mutmut_6 # type: ignore # mutmut generated
