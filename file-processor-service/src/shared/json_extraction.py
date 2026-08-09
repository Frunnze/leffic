from typing import TypeGuard

import demjson3

_OPENING_BRACE = "{"
_CLOSING_BRACE = "}"
_NOT_AN_OBJECT = "The model did not answer with an object"


def _is_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def get_dict_from_text(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)
