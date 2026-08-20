import secrets
from collections.abc import Sequence
from datetime import datetime
from typing import TypeGuard

from shared.models import Flashcard

_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_CORRECT_OPTION_ID = 0
_CORRECT = 1
_INCORRECT = 0
_TRUE_OR_FALSE = "true_or_false"
_SHORT_ANSWER = "short_answer"
_TRUE_LABEL = "True"
_FALSE_LABEL = "False"


def _is_object_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def date_to_str(dateobj: datetime) -> str:
    return dateobj.strftime(_DATE_FORMAT)


def flashcard_results(
    flashcards: Sequence[Flashcard],
) -> list[dict[str, object]]:
    return [
        {
            "id": flashcard.id,
            "type": flashcard.type,
            "next_review": (
                date_to_str(flashcard.next_review)
                if flashcard.next_review
                else None
            ),
            "content": flashcard.content,
            "created_at": date_to_str(flashcard.created_at),
            "fsrs_card": flashcard.fsrs_card,
        }
        for flashcard in flashcards
    ]


def prepare_content(
    content: dict[str, object], item_type: str
) -> dict[str, object]:
    if item_type == _TRUE_OR_FALSE:
        return _prepared_true_false_content(content)

    if item_type == _SHORT_ANSWER:
        return {"question": content.get("question"), "shuffled_options": []}

    return _prepared_options(content)


def _prepared_true_false_content(
    content: dict[str, object],
) -> dict[str, object]:
    is_true = bool(content.get("is_true"))
    correct = _TRUE_LABEL if is_true else _FALSE_LABEL
    wrong = _FALSE_LABEL if is_true else _TRUE_LABEL
    options: list[dict[str, object]] = [
        {"id": _CORRECT_OPTION_ID, "option": correct},
        {"id": _CORRECT_OPTION_ID + 1, "option": wrong},
    ]
    secrets.SystemRandom().shuffle(options)

    return {
        "question": content.get("statement"),
        "shuffled_options": options,
    }


def _prepared_options(content: dict[str, object]) -> dict[str, object]:
    true_options = [content.get("true_option")]
    options: list[dict[str, object]] = [
        {"id": index, "option": option}
        for index, option in enumerate(true_options)
    ]

    false_options = content.get("false_options")

    if _is_object_list(false_options):
        options.extend(
            {"id": index + len(true_options), "option": option}
            for index, option in enumerate(false_options)
        )

    secrets.SystemRandom().shuffle(options)

    return {
        "question": content.get("question"),
        "shuffled_options": options,
    }


def evaluate_accuracy(
    user_answers: Sequence[object],
    item_type: str,
    content: dict[str, object],
) -> int:
    if item_type == _SHORT_ANSWER:
        return _typed_accuracy(user_answers[0], content.get("answer"))

    if user_answers[0] == _CORRECT_OPTION_ID:
        return _CORRECT

    return _INCORRECT


def _typed_accuracy(typed: object, stored: object) -> int:
    if not isinstance(typed, str) or not isinstance(stored, str):
        return _INCORRECT

    if typed.strip().casefold() == stored.strip().casefold():
        return _CORRECT

    return _INCORRECT
