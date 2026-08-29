import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import (
    Folder,
    Test,
    TestItem,
    TestSession,
)
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_NOT_FOUND = 404

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
        quiz.test_items.append(TestItem(content=_QUESTION, type="mult_choice"))
        session.add(quiz)
        session.commit()

        return str(quiz.id)


def test_item_stats_count_the_correct_ones(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    _ = client.post(
        "/review-test-item",
        json={
            "test_item_id": item_id,
            "test_session": session_id,
            "answers": [0],
        },
        headers=authorization(),
    )

    response = client.get(
        "/test-items-stats",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, int]", response.json()) == {
        "total": 1,
        "correct": 1,
    }


def test_item_stats_report_nothing_without_items(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        session.add(Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID))
        session.commit()

    response = client.get(
        "/test-items-stats",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND


def test_an_owned_session_is_closed_and_scored(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    _ = client.post(
        "/review-test-item",
        json={
            "test_item_id": item_id,
            "test_session": session_id,
            "answers": [0],
        },
        headers=authorization(),
    )

    response = client.get(
        "/test-session-results",
        params={"test_session": session_id},
        headers=authorization(),
    )

    with sessions() as session:
        closed = session.query(TestSession).one()

    assert cast("dict[str, int]", response.json())["correct"] == 1
    assert closed.status == "done"
