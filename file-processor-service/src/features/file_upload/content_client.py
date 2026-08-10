import requests

from shared.settings import CONTENT_MANAGEMENT_SERVICE

_TIMEOUT_SECONDS = 60
_SAVE_FILE_NAMES = "/save-file-names"


def register_files(
    file_metadata: list[dict[str, str]], folder_id: str | None
) -> None:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{_SAVE_FILE_NAMES}",
        json={"file_metadata": file_metadata, "folder_id": folder_id},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
