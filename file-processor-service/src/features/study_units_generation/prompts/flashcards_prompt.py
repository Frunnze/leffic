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


def _output_format(flashcard_types: tuple[str, ...]) -> str:
    output_format = "{"

    for flashcard_type in flashcard_types:
        output_format += _TYPE_OUTPUT_FORMATS.get(flashcard_type, "")

    return output_format + _DECK_NAME_FORMAT + "}"


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
