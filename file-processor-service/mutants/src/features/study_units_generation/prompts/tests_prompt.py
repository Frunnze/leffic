_OUTPUT_FORMAT = """
    {
        "multiple_choice_test_items": [
            // these are multiple choice questions including true/false ones
            {
                "question": string, // a question or a statement
                "true_option": string, // the true option
                "false_options": list // a python list of false options
            }
        ],
        "test_name": string
        // a short name for the test; it has to include the word 'test'
    }
    """


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


def get_test_system_prompt() -> str:
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
    {_OUTPUT_FORMAT}
    ```

    ###Extracted text###
    """
