_DEFAULT_TYPES = ("basic",)

_TYPE_OUTPUT_FORMATS: dict[str, str] = {
    "basic": """
        "basic_flashcards": [
            {
                "front": string,
                // the front can be a question or a term or a foreign
                // word depending on the given extracted text
                "back": string
                // the back can be the answer, or the definition, or
                // the translation
            }
        ],""",
    "cloze": """
        "cloze_flashcards": [
            // also called fill in blank flashcards
            {
                "text": string,
                // the string from the given extracted text.
                // It has to match exactly!
                "hidden_parts": list
                // list of hidden words or phrases from the "text"
                // field taken verbatim, which are the most essential
                // for the learner to remember.
            }
        ],""",
    "list": """
        "list_flashcards": [
            // list flashcards are useful for remembering a list of
            // unordered but related items or ordered step-by-step
            // instructions or steps in an algorithm
            {
                "question": string, // this field is usually a question
                "items": list
                // list of items or steps to remember (similar to a
                // Python list of strings)
            }
        ],""",
}

_DECK_NAME_FORMAT = """
        "deck_name": string
        // a short name for the deck where the generated flashcards
        // will reside
    """


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__output_format__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__output_format__mutmut)
def _output_format(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_orig(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_1(flashcard_types: tuple[str, ...]) -> str:
    output_format = None

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_2(flashcard_types: tuple[str, ...]) -> str:
    output_format = "XX{XX"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_3(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format = _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_4(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format -= _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_5(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(None, "")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_6(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, None)

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_7(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get("")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_8(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, )

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_9(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "XXXX")

    return output_format + _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_10(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT - "}"


def x__output_format__mutmut_11(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format - _DECK_NAME_FORMAT + "}"


def x__output_format__mutmut_12(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "XX}XX"

mutants_x__output_format__mutmut['_mutmut_orig'] = x__output_format__mutmut_orig # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_1'] = x__output_format__mutmut_1 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_2'] = x__output_format__mutmut_2 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_3'] = x__output_format__mutmut_3 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_4'] = x__output_format__mutmut_4 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_5'] = x__output_format__mutmut_5 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_6'] = x__output_format__mutmut_6 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_7'] = x__output_format__mutmut_7 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_8'] = x__output_format__mutmut_8 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_9'] = x__output_format__mutmut_9 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_10'] = x__output_format__mutmut_10 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_11'] = x__output_format__mutmut_11 # type: ignore # mutmut generated
mutants_x__output_format__mutmut['x__output_format__mutmut_12'] = x__output_format__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_flashcards_system_prompt__mutmut)
def get_flashcards_system_prompt(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_orig(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_1(
    comprehensiveness: str = "XXmediumXX",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_2(
    comprehensiveness: str = "MEDIUM",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_3(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "XXlowXX",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_4(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "LOW",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_5(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = None

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_6(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else "XXXX"

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(flashcard_types)}
    ```

    ###Extracted text###
    """


def x_get_flashcards_system_prompt__mutmut_7(
    comprehensiveness: str = "medium",  # high, medium, low
    verbosity: str = "low",  # high, medium, low
    amount: int | None = None,
    flashcard_types: tuple[str, ...] = _DEFAULT_TYPES,  # basic, list, cloze
) -> str:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text
    by rigorously following the given constraints. It is highly
    important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and
    understand. Create flashcards starting with the most important
    information and progressing to the less important. Create the
    flashcards so the learner would understand the concepts as much as
    possible.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount_constraint}

    ###Output format###
    ```
    {_output_format(None)}
    ```

    ###Extracted text###
    """

mutants_x_get_flashcards_system_prompt__mutmut['_mutmut_orig'] = x_get_flashcards_system_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_1'] = x_get_flashcards_system_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_2'] = x_get_flashcards_system_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_3'] = x_get_flashcards_system_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_4'] = x_get_flashcards_system_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_5'] = x_get_flashcards_system_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_6'] = x_get_flashcards_system_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_flashcards_system_prompt__mutmut['x_get_flashcards_system_prompt__mutmut_7'] = x_get_flashcards_system_prompt__mutmut_7 # type: ignore # mutmut generated
