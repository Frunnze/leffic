import requests

from shared.json_extraction import get_dict_from_text
from shared.settings import CONTENT_MANAGEMENT_SERVICE

_TIMEOUT_SECONDS = 60


def save_study_unit(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        json=payload,
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)
