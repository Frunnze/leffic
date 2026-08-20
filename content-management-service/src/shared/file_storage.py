from pathlib import Path

_FILES_DIRECTORY = "files"


def delete_file_from_storage(filename: str) -> None:
    file_path = Path(_FILES_DIRECTORY) / filename

    if file_path.exists():
        file_path.unlink()
