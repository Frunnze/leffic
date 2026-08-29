import uuid
from typing import NamedTuple

from sqlalchemy.orm import Session

from shared.models import Folder, Test, TestItem

OK = 200
UNAUTHORIZED = 401
NOT_FOUND = 404
ONGOING = "ongoing"
DONE = "done"
MISSING_SESSION_DETAIL = "Test session does not exist!"
MISSING_FOLDER_DETAIL = "Folder does not exist!"
NO_TEST_STATS_DETAIL = "No test stats!"
CORRECT_ANSWER: list[object] = [0]
WRONG_ANSWER: list[object] = [1]

QUESTION: dict[str, object] = {
    "question": "Which is a mammal?",
    "true_option": "whale",
    "false_options": ["shark", "trout"],
}


class OwnedQuiz(NamedTuple):
    owner: uuid.UUID
    home_id: uuid.UUID
    folder_id: uuid.UUID
    test_id: uuid.UUID
    test_item_id: int


def seeded_quiz(session: Session, owner: uuid.UUID) -> OwnedQuiz:
    home = Folder(id=owner, name="Home", user_id=owner)
    session.add(home)
    session.flush()

    folder = Folder(name="Sub", user_id=owner, parent_id=home.id)
    session.add(folder)
    session.flush()

    quiz = Test(folder_id=folder.id, name="Quiz")
    quiz.test_items.append(TestItem(content=QUESTION, type="mult_choice"))
    session.add(quiz)
    session.commit()

    return OwnedQuiz(
        owner=owner,
        home_id=home.id,
        folder_id=folder.id,
        test_id=quiz.id,
        test_item_id=quiz.test_items[0].id,
    )


def review_body(
    test_item_id: int, test_session: uuid.UUID | str, answers: list[object]
) -> dict[str, object]:
    return {
        "test_item_id": test_item_id,
        "test_session": str(test_session),
        "answers": answers,
    }
