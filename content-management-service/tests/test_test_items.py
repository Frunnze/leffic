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
    TestItemReview,
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


def test_fetching_items_opens_a_session(
    client: TestClient, test_id: str
) -> None:
    response = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )

    body = cast("dict[str, object]", response.json())

    assert body["total_items"] == 1
    assert body["test_session"]


def test_fetching_items_reuses_an_open_session(
    client: TestClient, test_id: str
) -> None:
    first = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", first.json())["test_session"]

    second = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )

    assert cast("dict[str, str]", second.json())["test_session"] == session_id


def test_fetching_items_by_folder(client: TestClient, test_id: str) -> None:
    assert test_id

    response = client.get(
        "/test-items",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_items"] == 1


def test_fetching_items_needs_a_test_or_folder(client: TestClient) -> None:
    response = client.get("/test-items", headers=authorization())

    assert response.status_code == _NOT_FOUND


def test_reviewing_an_item_records_the_answer(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    response = client.post(
        "/review-test-item",
        json={
            "test_item_id": item_id,
            "test_session": session_id,
            "answers": [0],
        },
    )

    with sessions() as session:
        stored = session.query(TestItemReview).one()

    assert response.json() == {"msg": "Saved!"}
    assert stored.accuracy == 1


def test_reviewing_an_item_twice_updates_the_answer(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    payload = {
        "test_item_id": item_id,
        "test_session": session_id,
        "answers": [0],
    }
    _ = client.post("/review-test-item", json=payload)
    _ = client.post("/review-test-item", json={**payload, "answers": [1]})

    with sessions() as session:
        stored = session.query(TestItemReview).one()

    assert stored.accuracy == 0


def test_previous_answers_come_back_with_the_items(
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
    )

    again = client.get(
        "/test-items",
        params={"test_id": test_id, "test_session": session_id},
        headers=authorization(),
    )
    items = cast("dict[str, list[dict[str, object]]]", again.json())[
        "test_items"
    ]

    assert items[0]["last_answers"] == [0]
