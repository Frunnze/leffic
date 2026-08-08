from typing import TypeGuard

import demjson3

_OPENING_BRACE = "{"
_CLOSING_BRACE = "}"
_NOT_AN_OBJECT = "The model did not answer with an object"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


def _is_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)
mutants_x_get_dict_from_text__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_dict_from_text__mutmut)
def get_dict_from_text(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_orig(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_1(text: str) -> dict[str, object]:
    text = None
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_2(text: str) -> dict[str, object]:
    text = text.replace(None, "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_3(text: str) -> dict[str, object]:
    text = text.replace("\n", None)
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_4(text: str) -> dict[str, object]:
    text = text.replace("")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_5(text: str) -> dict[str, object]:
    text = text.replace("\n", )
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_6(text: str) -> dict[str, object]:
    text = text.replace("XX\nXX", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_7(text: str) -> dict[str, object]:
    text = text.replace("\n", "XXXX")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_8(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = None
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_9(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(None)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_10(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.rfind(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_11(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = None
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_12(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(None)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_13(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.find(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_14(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = None

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_15(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(None)

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_16(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index - 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_17(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 2])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_18(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(None):
        return decoded

    raise TypeError(_NOT_AN_OBJECT)


def x_get_dict_from_text__mutmut_19(text: str) -> dict[str, object]:
    text = text.replace("\n", "")
    start_index = text.find(_OPENING_BRACE)
    end_index = text.rfind(_CLOSING_BRACE)
    decoded = demjson3.decode(text[start_index : end_index + 1])

    if _is_object_dict(decoded):
        return decoded

    raise TypeError(None)

mutants_x_get_dict_from_text__mutmut['_mutmut_orig'] = x_get_dict_from_text__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_1'] = x_get_dict_from_text__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_2'] = x_get_dict_from_text__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_3'] = x_get_dict_from_text__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_4'] = x_get_dict_from_text__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_5'] = x_get_dict_from_text__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_6'] = x_get_dict_from_text__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_7'] = x_get_dict_from_text__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_8'] = x_get_dict_from_text__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_9'] = x_get_dict_from_text__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_10'] = x_get_dict_from_text__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_11'] = x_get_dict_from_text__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_12'] = x_get_dict_from_text__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_13'] = x_get_dict_from_text__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_14'] = x_get_dict_from_text__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_15'] = x_get_dict_from_text__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_16'] = x_get_dict_from_text__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_17'] = x_get_dict_from_text__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_18'] = x_get_dict_from_text__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_dict_from_text__mutmut['x_get_dict_from_text__mutmut_19'] = x_get_dict_from_text__mutmut_19 # type: ignore # mutmut generated
