import demjson3

_OPENING_BRACE = "{"
_CLOSING_BRACE = "}"


def get_dict_from_text(text: str) -> object:
    text = text.replace("\n", "").replace("\t", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)

    return demjson3.decode(text[start_index : end_index + 1])
