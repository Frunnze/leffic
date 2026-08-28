from pathlib import Path

_FILES_DIRECTORY = "files"


def storage_name(file_id: str, extension: str) -> str:
    if not extension:
        return file_id

    return f"{file_id}.{extension}"


def delete_file_from_storage(filename: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / filename

    if file_path.exists():
        file_path.unlink()
