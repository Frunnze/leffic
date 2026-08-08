import secrets
from collections.abc import Sequence
from datetime import datetime
from typing import TypeGuard

from shared.models import Flashcard

_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_CORRECT_OPTION_ID = 0
_CORRECT = 1
_INCORRECT = 0


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


def prepare_content(content: dict[str, object]) -> dict[str, object]:
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


def evaluate_accuracy(user_answers: Sequence[object]) -> int:
    if user_answers[0] == _CORRECT_OPTION_ID:
        return _CORRECT

    return _INCORRECT
