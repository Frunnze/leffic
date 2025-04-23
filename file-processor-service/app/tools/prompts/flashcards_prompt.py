def get_flashcards_system_prompt(
        comprehensiveness="medium", # high, medium, low
        verbosity="low", # high, medium, low
        amount=None,
        flashcard_types=["basic"] # basic, list, cloze
    ):
    if amount:
        amount = f"- Flashcards number: {amount};"
    else:
        amount = ""

    flashcard_types_output_formats = {
        "basic": """
        "basic_flashcards": [
            {
                "front": string, // the front can be a question or a term or a foreign word depending on the given extracted text
                "back": string // the back can be the answer, or the definition, or the translation
            }
        ],""",

        "cloze": """
        "cloze_flashcards": [ // also called fill in blank flashcards
            {
                "text": string, // the string from the given extracted text. It has to match exactly!
                "hidden_parts": list, // list of hidden words or phrases from the "text" field taken verbatim, which are the most essential for the learner to remember.
            }
        ],""",

        "list": """
        "list_flashcards": [ // list flashcards are useful for remembering a list of unordered but related items or ordered step-by-step instructions or steps in an algorithm
            {
                "question": string, // this field is usually a question
                "items": list // list of items or steps to remember (similar to a Python list of strings)
            }
        ],
        """
    }

    output_format = "{"
    for flashcard_type in flashcard_types:
        output_format += flashcard_types_output_formats.get(flashcard_type)
    output_format += """
        "deck_name": string // a short name for the deck where the generated flashcards will reside
    """
    output_format += "}"

    flashcards_system_prompt = f"""
    ###Role###
    You are an expert in creating flashcards. Your flashcards
    are extremely helpful in learning information.

    ###Task###
    Your task is to create flashcards based on the given extracted text by rigorously following the
    given constraints. It is highly important that each of the mentioned constraints is followed as
    specified. The flashcards have to be easy to remember and understand. Create flashcards starting 
    with the most important information and progressing to the less important.

    ###Constraints###
    - Comprehensiveness: {comprehensiveness};
    - Flashcard verbosity: {verbosity};
    {amount}

    ###Output format###
    ```
    {output_format}
    ```

    ###Extracted text###
    """

    return flashcards_system_prompt


if __name__ == "__main__":
    print(get_flashcards_system_prompt())

    system_prompt_template = """
    ###Role###
    You are an expert in creating flashcards.

    ###Task###

    ###Constraints###

    ###Output format###

    ###Context###
    """