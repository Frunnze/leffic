import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.study_units.formatting import (
    evaluate_accuracy,
    prepare_content,
)
from shared.database import get_db
from shared.models import (
    Folder,
    Test,
    TestItem,
)
from tests.support import (
    USER_ID,
    SessionProvider,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)
_QUESTION: dict[str, object] = {
    "question": "Which is a mammal?",
    "true_option": "whale",
    "false_options": ["shark", "trout"],
}


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
        session.add(folder)
        quiz = Test(folder_id=folder.id, name="Quiz")
        quiz.test_items.append(
            TestItem(content=_QUESTION, type="mult_choice")
        )
        session.add(quiz)
        session.commit()

        return str(quiz.id)


def test_prepare_content_shuffles_and_ids_the_options() -> None:
    prepared = prepare_content(_QUESTION, "multiple_choice")
    options = cast("list[dict[str, object]]", prepared["shuffled_options"])
    by_id = {int(str(option["id"])): option["option"] for option in options}

    assert set(prepared) == {"question", "shuffled_options"}
    assert prepared["question"] == _QUESTION["question"]
    assert by_id == {0: "whale", 1: "shark", 2: "trout"}
    assert set(options[0]) == {"id", "option"}


def test_prepare_content_copes_without_false_options() -> None:
    prepared = prepare_content(
        {"question": "q", "true_option": "a"}, "multiple_choice"
    )
    options = cast("list[dict[str, object]]", prepared["shuffled_options"])

    assert options == [{"id": 0, "option": "a"}]


def test_prepare_content_without_a_true_option() -> None:
    prepared = prepare_content(
        {"question": "q", "false_options": ["b"]}, "multiple_choice"
    )
    options = cast("list[dict[str, object]]", prepared["shuffled_options"])
    by_id = {int(str(option["id"])): option["option"] for option in options}

    assert by_id == {0: None, 1: "b"}


def test_the_true_option_scores_one() -> None:
    assert evaluate_accuracy([0], "multiple_choice", {}) == 1


def test_any_other_option_scores_zero() -> None:
    assert evaluate_accuracy([2], "multiple_choice", {}) == 0

