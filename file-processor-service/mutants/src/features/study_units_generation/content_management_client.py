import requests

from shared.json_extraction import get_dict_from_text
from shared.settings import CONTENT_MANAGEMENT_SERVICE

_TIMEOUT_SECONDS = 60


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_save_study_unit__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_save_study_unit__mutmut)
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


def x_save_study_unit__mutmut_orig(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        json=payload,
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_1(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = None
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_2(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=None,
        json=payload,
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_3(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        json=None,
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_4(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        json=payload,
        timeout=None,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_5(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        json=payload,
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_6(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_7(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        json=payload,
        )
    response.raise_for_status()

    return get_dict_from_text(response.text)


def x_save_study_unit__mutmut_8(
    path: str, payload: dict[str, object]
) -> dict[str, object]:
    response = requests.post(
        url=f"{CONTENT_MANAGEMENT_SERVICE}{path}",
        json=payload,
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return get_dict_from_text(None)

mutants_x_save_study_unit__mutmut['_mutmut_orig'] = x_save_study_unit__mutmut_orig # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_1'] = x_save_study_unit__mutmut_1 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_2'] = x_save_study_unit__mutmut_2 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_3'] = x_save_study_unit__mutmut_3 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_4'] = x_save_study_unit__mutmut_4 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_5'] = x_save_study_unit__mutmut_5 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_6'] = x_save_study_unit__mutmut_6 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_7'] = x_save_study_unit__mutmut_7 # type: ignore # mutmut generated
mutants_x_save_study_unit__mutmut['x_save_study_unit__mutmut_8'] = x_save_study_unit__mutmut_8 # type: ignore # mutmut generated
