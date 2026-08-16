from collections.abc import Mapping
from pathlib import Path
from string import Template

_PROMPT_FILES = Path(__file__).parent / "prompt_files"
_PROMPT_SUFFIX = ".md"
_UNKNOWN_PROMPT = "No prompt file named"


class MissingPromptFileError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"{_UNKNOWN_PROMPT} {name}{_PROMPT_SUFFIX}")


def rendered_prompt(name: str, values: Mapping[str, str]) -> str:
    prompt_file = _PROMPT_FILES / f"{name}{_PROMPT_SUFFIX}"

    if not prompt_file.is_file():
        raise MissingPromptFileError(name)

    template = Template(prompt_file.read_bytes().decode())

    return template.substitute(**values)


def flashcard_values(
    comprehensiveness: str, verbosity: str, amount: int | None
) -> dict[str, str]:
    amount_constraint = f"- Flashcards number: {amount};" if amount else ""

    return {
        "comprehensiveness": comprehensiveness,
        "verbosity": verbosity,
        "amount_constraint": amount_constraint,
    }


def assessment_item_values(amount: int | None) -> dict[str, str]:
    amount_constraint = f"- Test items number: {amount};" if amount else ""

    return {"amount_constraint": amount_constraint}
