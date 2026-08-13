_DEFAULT_TYPES = ("multiple_choice",)

_TYPE_OUTPUT_FORMATS: dict[str, str] = {
    "multiple_choice": """
        "multiple_choice_test_items": [
            {
                "question": string, // a question or a statement
                "true_option": string, // the true option
                "false_options": list // a python list of false options
            }
        ],""",
    "true_or_false": """
        "true_or_false_test_items": [
            // a claim the learner judges; write some that are true and
            // some that are false, and make the false ones wrong in a
            // way the extracted text can settle
            {
                "statement": string,
                // one claim, stated plainly, never a question
                "is_true": boolean
                // whether the extracted text supports the statement
            }
        ],""",
    "short_answer": """
        "short_answer_test_items": [
            // the learner types the answer, which is compared with the
            // stored one, so the answer must be short and have only one
            // sensible wording
            {
                "question": string,
                // ask for a single term, name, date or number
                "answer": string
                // the expected answer, at most a few words
            }
        ],""",
}

_TEST_NAME_FORMAT = """
        "test_name": string
        // a short name for the test; it has to include the word 'test'
    """


def _output_format(test_item_types: tuple[str, ...]) -> str:
    known_types = tuple(
        item_type
        for item_type in test_item_types
        if item_type in _TYPE_OUTPUT_FORMATS
    )
    requested_types = known_types or _DEFAULT_TYPES

    output_format = "{"

    for item_type in requested_types:
        output_format += _TYPE_OUTPUT_FORMATS[item_type]

    return output_format + _TEST_NAME_FORMAT + "}"


def get_test_system_prompt(
    test_item_types: tuple[str, ...] = _DEFAULT_TYPES,
) -> str:
    return f"""
    ###Role###
    You are an expert in creating tests. Your tests
    are very helpful in assessing the learner's knowledge.
    In addition, your tests also help the user learn while the
    test is being completed.

    ###Task###
    Your task is to create tests items based on the given extracted text and
    strictly following the output format. Create the test items starting with
    the most important information and progressing to the less important.

    ###Output format###
    JSON```
    {_output_format(test_item_types)}
    ```

    ###Extracted text###
    """
